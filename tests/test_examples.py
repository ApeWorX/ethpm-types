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

    else:
        with pytest.raises((ValidationError, ValueError)):
            PackageManifest.parse_obj(example_json).dict()


def test_open_zeppelin_contracts():
    oz_manifest_file = Path(__file__).parent / "data" / "OpenZeppelinContracts.json"
    manifest_dict = json.loads(oz_manifest_file.read_text())
    package = PackageManifest.parse_obj(manifest_dict)
    assert package.dict() == manifest_dict
