import os

import github
import pytest  # type: ignore
import requests  # type: ignore
from pydantic import ValidationError

from ethpm import PackageManifest

# NOTE: Must export GITHUB_ACCESS_TOKEN
ETHPM_SPEC_REPO = github.Github(os.environ["GITHUB_ACCESS_TOKEN"]).get_repo("ethpm/ethpm-spec")

EXAMPLES_RAW_URL = "https://raw.githubusercontent.com/ethpm/ethpm-spec/master/examples"


@pytest.mark.parametrize(
    "example_name",
    [f.name for f in ETHPM_SPEC_REPO.get_contents("examples")],  # type: ignore
)
def test_uniswap_tokenlists(example_name):
    example = requests.get(f"{EXAMPLES_RAW_URL}/{example_name}/v3.json").json()

    if "invalid" not in example_name:
        assert PackageManifest.parse_obj(example).dict() == example

    else:
        with pytest.raises((ValidationError, ValueError)):
            PackageManifest.parse_obj(example).dict()
