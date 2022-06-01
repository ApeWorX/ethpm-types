import json
from pathlib import Path
from typing import Dict

import pytest
from eth_utils import keccak

from ethpm_types import ContractType
from ethpm_types.abi import ABI, EventABI, MethodABI

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


def _select_abi(contract_type: ContractType, name: str) -> ABI:
    for abi in contract_type.abi:
        abi_name = abi.name if hasattr(abi, "name") else None  # type: ignore
        if abi_name == name:
            return abi

    raise ValueError(f"No method found with name '{name}'.")


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
    assert array_output.canonical_type == "address[]"


def test_static_solidity_struct_arrays(solidity_contract):
    contract_type = ContractType.parse_obj(solidity_contract)
    method_abi = _select_abi(contract_type, "getStaticStructList")
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[2]"
    assert array_output.canonical_type == "(uint256,(address,bytes32))[2]"


def test_dynamic_solidity_struct_arrays(solidity_contract):
    contract_type = ContractType.parse_obj(solidity_contract)
    method_abi = _select_abi(contract_type, "getDynamicStructList")
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[]"
    assert array_output.canonical_type == "((address,bytes32),uint256)[]"


def test_static_vyper_struct_arrays(vyper_contract):
    # NOTE: Vyper struct arrays <=0.3.3 don't include struct info
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = [
        abi
        for abi in contract_type.abi
        if hasattr(abi, "name") and abi.name == "getStaticStructList"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "(uint256,(address,bytes32))[2]"
    assert array_output.canonical_type == "(uint256,(address,bytes32))[2]"


def test_dynamic_vyper_struct_arrays(vyper_contract):
    # NOTE: Vyper struct arrays <=0.3.3 don't include struct info
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = [
        abi
        for abi in contract_type.abi
        if hasattr(abi, "name") and abi.name == "getDynamicStructList"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "((address,bytes32),uint256)[]"
    assert array_output.canonical_type == "((address,bytes32),uint256)[]"


def test_select_by_name(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    for selector in ["setNumber", "setNumber(uint256)", keccak(text="setNumber(uint256)")]:
        method = contract_type.mutable_methods[selector]
        assert isinstance(method, MethodABI)
        assert method.name == "setNumber"

    for selector in ["getStruct", "getStruct()", keccak(text="getStruct()")]:
        view = contract_type.view_methods[selector]
        assert isinstance(view, MethodABI)
        assert view.name == "getStruct"

    for selector in [
        "NumberChange",
        "NumberChange(uint256,uint256)",
        keccak(text="NumberChange(uint256,uint256)"),
    ]:
        event = contract_type.events[selector]
        assert isinstance(event, EventABI)
        assert event.name == "NumberChange"


def test_select_by_name_contains(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    assert "setNumber" in contract_type.mutable_methods
    assert "setNumber(uint256)" in contract_type.mutable_methods
    assert keccak(text="setNumber(uint256)") in contract_type.mutable_methods
    assert "madeUpFunction" not in contract_type.mutable_methods

    assert "getStruct" in contract_type.view_methods
    assert "getStruct()" in contract_type.view_methods
    assert keccak(text="getStruct()") in contract_type.view_methods
    assert "madeUpFunction(uint64)" not in contract_type.view_methods

    assert "NumberChange" in contract_type.events
    assert "NumberChange(uint256,uint256)" in contract_type.events
    assert keccak(text="NumberChange(uint256,uint256)") in contract_type.events
    assert keccak(text="MadeUpEvent(uint64)") not in contract_type.events
