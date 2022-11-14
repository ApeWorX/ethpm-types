import json
from pathlib import Path

import pytest

from ethpm_types import PackageManifest


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
