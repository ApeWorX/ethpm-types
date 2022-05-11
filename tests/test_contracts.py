import json
from pathlib import Path
from typing import Dict

import pytest

from ethpm_types import ContractType
from ethpm_types.abi import MethodABI

CONTRACT_NAMES = ("SolidityContract.json", "VyperContract.json")
DATA_FILES = {
    p.name: p for p in (Path(__file__).parent / "data").iterdir() if p.name in CONTRACT_NAMES
}


@pytest.fixture
def solidity_contract():
    return _get_contract(CONTRACT_NAMES[0])


@pytest.fixture
def vyper_contract():
    return _get_contract(CONTRACT_NAMES[1])


@pytest.fixture(params=CONTRACT_NAMES)
def contract(request):
    yield _get_contract(request.param)


def _get_contract(name: str) -> Dict:
    return json.loads(DATA_FILES[name].read_text())


def _select_abi(contract_type: ContractType, name: str) -> MethodABI:
    return [abi for abi in contract_type.abi if hasattr(abi, "name") and abi.name == name][0]


def test_structs(contract):
    contract_type = ContractType.parse_obj(contract)
    method_abi = _select_abi(contract_type, "getStruct")
    assert len(method_abi.outputs) == 1
    output = method_abi.outputs[0]
    assert output.type == "tuple"
    assert len(output.components) == 2


def test_solidity_address_arrays(solidity_contract):
    contract_type = ContractType.parse_obj(solidity_contract)
    method_abi = _select_abi(contract_type, "getAddressList")
    assert len(method_abi.outputs) == 1
    array_output = method_abi.outputs[0]
    assert array_output.type == "address[2]"


def test_vyper_address_arrays(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = _select_abi(contract_type, "getAddressList")
    assert len(method_abi.outputs) == 1
    array_output = method_abi.outputs[0]
    assert array_output.type == "address[]"


def test_solidity_struct_arrays(solidity_contract):
    contract_type = ContractType.parse_obj(solidity_contract)
    method_abi = _select_abi(contract_type, "getStructList")
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[2]"
    assert array_output.canonical_type == "((address,bytes32),uint256)"


def test_vyper_struct_arrays(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = [
        abi for abi in contract_type.abi if hasattr(abi, "name") and abi.name == "getStructList"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "((address,bytes32),uint256)[]"
    assert array_output.canonical_type == "((address,bytes32),uint256)[]"
