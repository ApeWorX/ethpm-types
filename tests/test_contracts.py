import json
from pathlib import Path

import pytest

from ethpm_types import ContractType

CONTRACT_NAMES = ("SolidityContract.json", "VyperContract.json")
DATA_FILES = {
    p.name: p for p in (Path(__file__).parent / "data").iterdir() if p.name in CONTRACT_NAMES
}


@pytest.fixture
def solidity_contract():
    return json.loads(DATA_FILES[CONTRACT_NAMES[0]].read_text())


@pytest.fixture
def vyper_contract():
    return json.loads(DATA_FILES[CONTRACT_NAMES[1]].read_text())


def test_solidity_array_of_structs(solidity_contract):
    contract_type = ContractType.parse_obj(solidity_contract)
    method_abi = [
        abi for abi in contract_type.abi if hasattr(abi, "name") and abi.name == "getStructList"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[2]"
    assert array_output.canonical_type == "((address,bytes32),uint256)"


def test_vyper_array_of_structs(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = [
        abi for abi in contract_type.abi if hasattr(abi, "name") and abi.name == "getStructList"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "((address,bytes32),uint256)[]"
    assert array_output.canonical_type == "((address,bytes32),uint256)[]"
