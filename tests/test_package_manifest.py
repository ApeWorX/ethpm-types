import os

import github
import pytest
import requests
from pydantic import ValidationError

from ethpm_types import PackageManifest

ETHPM_SPEC_REPO = github.Github(os.environ.get("GITHUB_ACCESS_TOKEN", None)).get_repo(
    "ethpm/ethpm-spec"
)

EXAMPLES_RAW_URL = "https://raw.githubusercontent.com/ethpm/ethpm-spec/master/examples"


@pytest.mark.parametrize(
    "example_name",
    [f.name for f in ETHPM_SPEC_REPO.get_contents("examples")],  # type: ignore[union-attr]
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
        with pytest.raises(ValidationError):
            PackageManifest.parse_obj(example_json).dict()


def test_open_zeppelin_contracts(oz_package, oz_package_manifest_dict):
    assert oz_package.dict() == oz_package_manifest_dict

    for source_name, source in oz_package.sources.items():
        # NOTE: Per EIP-2678, "Checksum is only required if content is missing"
        if not source.content:
            assert source.content_is_valid(), f"Invalid checksum for '{source_name}'"


def test_file_bases_dependency_url():
    manifest = PackageManifest(
        buildDependencies={"test-package": "file:///path/to/manifest/test-package.json"}
    )
    assert manifest.dependencies["test-package"] == "file:///path/to/manifest/test-package.json"
