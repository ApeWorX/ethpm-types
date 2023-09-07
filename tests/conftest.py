from pathlib import Path

import pytest

from ethpm_types import ContractType, PackageManifest, Source

BASE = Path(__file__).parent / "data"
COMPILED_BASE = BASE / "Compiled"
SOURCE_BASE = BASE / "Sources"
SOURCE_ID = "VyperContract.vy"


@pytest.fixture
def get_contract_type():
    def fn(name: str) -> ContractType:
        return ContractType.parse_file(COMPILED_BASE / f"{name}.json")

    return fn


@pytest.fixture
def oz_package_manifest_path():
    return COMPILED_BASE / "OpenZeppelinContracts.json"


@pytest.fixture
def oz_package(oz_package_manifest_path):
    return PackageManifest.parse_file(oz_package_manifest_path)


@pytest.fixture
def source_base() -> Path:
    return SOURCE_BASE


@pytest.fixture
def oz_contract_type(oz_package):
    # NOTE: AccessControl has events, view methods, and mutable methods.
    return oz_package.contract_types["AccessControl"]


@pytest.fixture
def content_raw() -> str:
    return (SOURCE_BASE / "VyperContract.vy").read_text()


@pytest.fixture
def source(content_raw) -> Source:
    return Source.parse_obj({"source_id": SOURCE_ID, "content": content_raw})


@pytest.fixture
def content(source):
    return source.content


@pytest.fixture
def vyper_contract(get_contract_type):
    return get_contract_type("VyperContract")


@pytest.fixture
def solidity_contract(get_contract_type):
    return get_contract_type("SolidityContract")


@pytest.fixture
def contract_with_error(get_contract_type):
    return get_contract_type("HasError")


@pytest.fixture(params=("Vyper", "Solidity"))
def contract(request, get_contract_type):
    yield get_contract_type(f"{request.param}Contract")


@pytest.fixture
def solidity_fallback_and_receive_contract(get_contract_type):
    return get_contract_type("SolFallbackAndReceive")


@pytest.fixture
def vyper_default_contract(get_contract_type):
    return get_contract_type("VyDefault")


@pytest.fixture(params=("Vyper", "Solidity"))
def fallback_contract(request, get_contract_type):
    key = "VyDefault" if request.param == "Vyper" else "SolFallbackAndReceive"
    return get_contract_type(key)


@pytest.fixture
def package_manifest(solidity_contract, vyper_contract):
    return PackageManifest(
        contractTypes={
            solidity_contract.name: solidity_contract,
            vyper_contract.name: vyper_contract,
        },
        sources={solidity_contract.source_id: "", vyper_contract.source_id: ""},
    )
