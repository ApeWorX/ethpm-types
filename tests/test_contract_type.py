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
MUTABLE_METHOD_SELECTOR_BYTES = keccak(text="setNumber(uint256)")
VIEW_METHOD_SELECTOR_BYTES = keccak(text="getStruct()")
EVENT_SELECTOR_BYTES = keccak(text="NumberChange(uint256,uint256)")


view_selector_parametrization = pytest.mark.parametrize(
    "selector",
    (
        "getStruct",
        "getStruct()",
        VIEW_METHOD_SELECTOR_BYTES,
        VIEW_METHOD_SELECTOR_BYTES[:32],
        f"0x{VIEW_METHOD_SELECTOR_BYTES.hex()}",
        f"0x{VIEW_METHOD_SELECTOR_BYTES[:32].hex()}",
    ),
)
mutable_selector_parametrization = pytest.mark.parametrize(
    "selector",
    (
        "setNumber",
        "setNumber(uint256)",
        MUTABLE_METHOD_SELECTOR_BYTES,
        MUTABLE_METHOD_SELECTOR_BYTES[:32],
        f"0x{MUTABLE_METHOD_SELECTOR_BYTES.hex()}",
        f"0x{MUTABLE_METHOD_SELECTOR_BYTES[:32].hex()}",
    ),
)
event_selector_parametrization = pytest.mark.parametrize(
    "selector",
    (
        "NumberChange",
        "NumberChange(uint256,uint256)",
        EVENT_SELECTOR_BYTES,
        EVENT_SELECTOR_BYTES[:32],
        f"0x{EVENT_SELECTOR_BYTES.hex()}",
        f"0x{EVENT_SELECTOR_BYTES[:32].hex()}",
    ),
)


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
        abi_name = abi.name if hasattr(abi, "name") else None
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


@mutable_selector_parametrization
def test_select_mutable_method_by_name_and_selectors(selector, vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    assert selector in contract_type.mutable_methods
    method = contract_type.mutable_methods[selector]
    assert isinstance(method, MethodABI)
    assert method.name == "setNumber"


@view_selector_parametrization
def test_select_view_method_by_name_and_selectors(selector, vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    assert selector in contract_type.view_methods
    view = contract_type.view_methods[selector]
    assert isinstance(view, MethodABI)
    assert view.name == "getStruct"


@event_selector_parametrization
def test_select_and_contains_event_by_name_and_selectors(selector, vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    assert selector in contract_type.events
    event = contract_type.events[selector]
    assert isinstance(event, EventABI)
    assert event.name == "NumberChange"


def test_select_and_contains_by_abi(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    event = contract_type.events[0]
    view = contract_type.view_methods[0]
    mutable = contract_type.mutable_methods[0]
    assert contract_type.events[event] == event
    assert contract_type.view_methods[view] == view
    assert contract_type.mutable_methods[mutable] == mutable
    assert event in contract_type.events
    assert view in contract_type.view_methods
    assert mutable in contract_type.mutable_methods


def test_select_by_slice(oz_contract_type):
    events = [x.name for x in oz_contract_type.events[:2]]
    views = [x.name for x in oz_contract_type.view_methods[:2]]
    mutables = [x.name for x in oz_contract_type.mutable_methods[:2]]
    assert events == ["RoleAdminChanged", "RoleGranted"]
    assert views == ["DEFAULT_ADMIN_ROLE", "getRoleAdmin"]
    assert mutables == ["grantRole", "renounceRole"]


def test_contract_type_excluded_in_repr_abi(vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    actual = repr(contract_type.events[0])
    assert "contract_type" not in actual

    actual = repr(contract_type.mutable_methods[0])
    assert "contract_type" not in actual

    actual = repr(contract_type.view_methods[0])
    assert "contract_type" not in actual


def test_contract_type_backrefs(oz_contract_type):
    assert oz_contract_type.events, "setup: Test contract should have events"
    assert oz_contract_type.view_methods, "setup: Test contract should have view methods"
    assert oz_contract_type.mutable_methods, "setup: Test contract should have mutable methods"

    assert oz_contract_type.constructor.contract_type == oz_contract_type
    assert oz_contract_type.fallback.contract_type == oz_contract_type
    assert all(e.contract_type == oz_contract_type for e in oz_contract_type.events)
    assert all(m.contract_type == oz_contract_type for m in oz_contract_type.mutable_methods)
    assert all(m.contract_type == oz_contract_type for m in oz_contract_type.view_methods)


@view_selector_parametrization
def test_select_view_method_from_all_methods(selector, vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = contract_type.methods[selector]
    assert method_abi.selector == "getStruct()"


@mutable_selector_parametrization
def test_select_mutable_method_from_all_methods(selector, vyper_contract):
    contract_type = ContractType.parse_obj(vyper_contract)
    method_abi = contract_type.methods[selector]
    assert method_abi.selector == "setNumber(uint256)"


def test_repr(vyper_contract):
    contract = ContractType.parse_obj(vyper_contract)
    assert repr(contract) == "<ContractType TestContractVy>"

    contract.name = None
    assert repr(contract) == "<ContractType>"
