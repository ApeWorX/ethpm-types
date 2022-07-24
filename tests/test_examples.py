import json
import os
from pathlib import Path

import github
import pytest  # type: ignore
import requests  # type: ignore
from pydantic import ValidationError

from ethpm_types import PackageManifest

ETHPM_SPEC_REPO = github.Github(os.environ.get("GITHUB_ACCESS_TOKEN", None)).get_repo(
    "ethpm/ethpm-spec"
)

EXAMPLES_RAW_URL = "https://raw.githubusercontent.com/ethpm/ethpm-spec/master/examples"


@pytest.fixture
def oz_package_manifest_dict():
    oz_manifest_file = Path(__file__).parent / "data" / "OpenZeppelinContracts.json"
    return json.loads(oz_manifest_file.read_text())


@pytest.fixture
def oz_package(oz_package_manifest_dict):
    return PackageManifest.parse_obj(oz_package_manifest_dict)


@pytest.fixture
def oz_contract_type(oz_package):
    # NOTE: AccessControl has events, view methods, and mutable methods.
    return oz_package.contract_types["AccessControl"]


@pytest.mark.parametrize(
    "example_name",
    [f.name for f in ETHPM_SPEC_REPO.get_contents("examples")],  # type: ignore
)
def test_examples(example_name):
    example = requests.get(f"{EXAMPLES_RAW_URL}/{example_name}/v3.json")
    example_json = example.json()

    if "invalid" not in example_name:
        package = PackageManifest.parse_obj(example_json)
        assert package.dict() == example_json

        # NOTE: Also make sure that the encoding is exactly the same (per EIP-2678)
        assert package.json() == example.text

        if package.sources:
            for source_name, source in package.sources.items():
                # NOTE: Per EIP-2678, "Checksum is only required if content is missing"
                if not source.content:
                    assert source.content_is_valid(), f"Invalid checksum for '{source_name}'"

    else:
        with pytest.raises((ValidationError, ValueError)):
            PackageManifest.parse_obj(example_json).dict()


def test_open_zeppelin_contracts(oz_package, oz_package_manifest_dict):
    assert oz_package.dict() == oz_package_manifest_dict

    for source_name, source in oz_package.sources.items():
        # NOTE: Per EIP-2678, "Checksum is only required if content is missing"
        if not source.content:
            assert source.content_is_valid(), f"Invalid checksum for '{source_name}'"


def test_contract_type_backrefs(oz_contract_type):
    assert oz_contract_type.events, "setup: Test contract should have events"
    assert oz_contract_type.view_methods, "setup: Test contract should have view methods"
    assert oz_contract_type.mutable_methods, "setup: Test contract should have mutable methods"

    assert oz_contract_type.constructor.contract_type == oz_contract_type
    assert oz_contract_type.fallback.contract_type == oz_contract_type
    assert all(e.contract_type == oz_contract_type for e in oz_contract_type.events)
    assert all(m.contract_type == oz_contract_type for m in oz_contract_type.mutable_methods)
    assert all(m.contract_type == oz_contract_type for m in oz_contract_type.view_methods)
