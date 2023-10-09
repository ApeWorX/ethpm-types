import pytest
from eth_utils import keccak

from ethpm_types import ContractType, HexBytes
from ethpm_types.abi import ABI, ErrorABI, EventABI, MethodABI

MUTABLE_METHOD_SELECTOR_BYTES = keccak(text="setNumber(uint256)")
VIEW_METHOD_SELECTOR_BYTES = keccak(text="getStruct()")
EVENT_SELECTOR_STRING = "NumberChange(bytes32,uint256,string,uint256,string)"
EVENT_SELECTOR_BYTES = keccak(text=EVENT_SELECTOR_STRING)
ERROR_SELECTOR_STRING = "Unauthorized(address,uint256)"
ERROR_SELECTOR_BYTES = keccak(text=ERROR_SELECTOR_STRING)


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
        EVENT_SELECTOR_STRING,
        EVENT_SELECTOR_BYTES,
        EVENT_SELECTOR_BYTES[:32],
        f"0x{EVENT_SELECTOR_BYTES.hex()}",
        f"0x{EVENT_SELECTOR_BYTES[:32].hex()}",
    ),
)
error_selector_parametrization = pytest.mark.parametrize(
    "selector",
    (
        "Unauthorized",
        ERROR_SELECTOR_STRING,
        ERROR_SELECTOR_BYTES,
        ERROR_SELECTOR_BYTES[:32],
        f"0x{ERROR_SELECTOR_BYTES.hex()}",
        f"0x{ERROR_SELECTOR_BYTES[:32].hex()}",
    ),
)


def _select_abi(contract_type: ContractType, name: str) -> ABI:
    for abi in contract_type.abi:
        abi_name = abi.name if hasattr(abi, "name") else None
        if abi_name == name:
            return abi

    raise AssertionError(f"No method found with name '{name}'.")


def test_structs(contract):
    method_abi = _select_abi(contract, "getStruct")
    assert contract.structs == []
    assert len(method_abi.outputs) == 1
    output = method_abi.outputs[0]
    assert output.type == "tuple"
    assert len(output.components) == 2


def test_solidity_address_arrays(solidity_contract):
    method_abi = _select_abi(solidity_contract, "getAddressArray")
    assert len(method_abi.outputs) == 1
    array_output = method_abi.outputs[0]
    assert array_output.type == "address[2]"


def test_vyper_address_arrays(vyper_contract):
    method_abi = _select_abi(vyper_contract, "getAddressArray")
    assert len(method_abi.outputs) == 1
    array_output = method_abi.outputs[0]
    assert array_output.type == "address[]"
    assert array_output.canonical_type == "address[]"


def test_static_solidity_struct_arrays(solidity_contract):
    method_abi = _select_abi(solidity_contract, "getStaticStructArray")
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[3]"
    assert array_output.canonical_type == "(uint256,(address,bytes32))[3]"


def test_dynamic_solidity_struct_arrays(solidity_contract):
    method_abi = _select_abi(solidity_contract, "getDynamicStructArray")
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[]"
    assert array_output.canonical_type == "((address,bytes32),uint256)[]"


def test_static_vyper_struct_arrays(vyper_contract):
    # NOTE: Vyper struct arrays <=0.3.3 don't include struct info
    method_abi = [
        abi
        for abi in vyper_contract.abi
        if hasattr(abi, "name") and abi.name == "getStaticStructArray"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[2]"
    assert array_output.canonical_type == "(uint256,(address,bytes32))[2]"


def test_dynamic_vyper_struct_arrays(vyper_contract):
    # NOTE: Vyper struct arrays <=0.3.3 don't include struct info
    method_abi = [
        abi
        for abi in vyper_contract.abi
        if hasattr(abi, "name") and abi.name == "getDynamicStructArray"
    ][0]
    array_output = method_abi.outputs[0]
    assert array_output.type == "tuple[]"
    assert array_output.canonical_type == "((address,bytes32),uint256)[]"


@mutable_selector_parametrization
def test_select_mutable_method_by_name_and_selectors(selector, vyper_contract):
    assert selector in vyper_contract.mutable_methods
    method = vyper_contract.mutable_methods[selector]
    assert isinstance(method, MethodABI)
    assert method.name == "setNumber"


@view_selector_parametrization
def test_select_view_method_by_name_and_selectors(selector, vyper_contract):
    assert selector in vyper_contract.view_methods
    view = vyper_contract.view_methods[selector]
    assert isinstance(view, MethodABI)
    assert view.name == "getStruct"


@event_selector_parametrization
def test_select_and_contains_event_by_name_and_selectors(selector, vyper_contract):
    assert selector in vyper_contract.events
    event = vyper_contract.events[selector]
    assert isinstance(event, EventABI)
    assert event.name == "NumberChange"


@error_selector_parametrization
def test_select_and_contains_error_by_name_and_selectors(selector, contract_with_error):
    assert selector in contract_with_error.errors
    event = contract_with_error.errors[selector]
    assert isinstance(event, ErrorABI)
    assert event.name == "Unauthorized"


def test_select_and_contains_by_abi(vyper_contract):
    event = vyper_contract.events[0]
    view = vyper_contract.view_methods[0]
    mutable = vyper_contract.mutable_methods[0]
    assert vyper_contract.events[event] == event
    assert vyper_contract.view_methods[view] == view
    assert vyper_contract.mutable_methods[mutable] == mutable
    assert event in vyper_contract.events
    assert view in vyper_contract.view_methods
    assert mutable in vyper_contract.mutable_methods


def test_select_by_slice(oz_contract_type):
    events = [x.name for x in oz_contract_type.events[:2]]
    views = [x.name for x in oz_contract_type.view_methods[:2]]
    mutables = [x.name for x in oz_contract_type.mutable_methods[:2]]
    assert events == ["RoleAdminChanged", "RoleGranted"]
    assert views == ["DEFAULT_ADMIN_ROLE", "getRoleAdmin"]
    assert mutables == ["grantRole", "renounceRole"]


def test_contract_type_excluded_in_repr_abi(vyper_contract):
    actual = repr(vyper_contract.events[0])
    assert "contract_type" not in actual

    actual = repr(vyper_contract.mutable_methods[0])
    assert "contract_type" not in actual

    actual = repr(vyper_contract.view_methods[0])
    assert "contract_type" not in actual


def test_contract_type_backrefs(oz_contract_type):
    assert oz_contract_type.events, "setup: Test contract should have events"
    assert oz_contract_type.view_methods, "setup: Test contract should have view methods"
    assert oz_contract_type.mutable_methods, "setup: Test contract should have mutable methods"

    assert oz_contract_type.constructor.contract_type == oz_contract_type
    assert all(e.contract_type == oz_contract_type for e in oz_contract_type.events)
    assert all(m.contract_type == oz_contract_type for m in oz_contract_type.mutable_methods)
    assert all(m.contract_type == oz_contract_type for m in oz_contract_type.view_methods)


@view_selector_parametrization
def test_select_view_method_from_all_methods(selector, vyper_contract):
    method_abi = vyper_contract.methods[selector]
    assert method_abi.selector == "getStruct()"


@mutable_selector_parametrization
def test_select_mutable_method_from_all_methods(selector, vyper_contract):
    method_abi = vyper_contract.methods[selector]
    assert method_abi.selector == "setNumber(uint256)"


def test_repr(vyper_contract):
    assert repr(vyper_contract) == "<ContractType VyperContract>"

    vyper_contract.name = None
    assert repr(vyper_contract) == "<ContractType>"


def test_solidity_fallback_and_receive(solidity_fallback_and_receive_contract):
    """
    Ensure we can detect the fallback and receive methods when they are defined.
    For solidity, you can define both.
    """
    assert solidity_fallback_and_receive_contract.fallback.type == "fallback"
    assert solidity_fallback_and_receive_contract.receive.type == "receive"

    # Typically, if receive is defined, fallback is non-payable.
    # Though, that is not always the case.
    assert solidity_fallback_and_receive_contract.fallback.stateMutability == "nonpayable"


def test_vyper_default(vyper_default_contract):
    """
    Ensure the Vyper default method shows up as the fallback method in the contract.
    """
    assert vyper_default_contract.fallback.type == "fallback"


def test_fallback_and_receive_not_defined(contract):
    """
    Ensure that when the fallback method is not defined, in a Solidity contract,
    it is None. Same with the receive method. Runs for both Solidity and Vyper.
    """

    # Both `VyperContract` and `SolidityContract` do not define these.
    assert contract.receive is None
    assert contract.fallback is None


def test_init_using_bytes(contract):
    raw_bytes = HexBytes(contract.deployment_bytecode.bytecode)
    new_contract = ContractType(abi=[], deploymentBytecode=raw_bytes)
    assert new_contract.deployment_bytecode.bytecode == raw_bytes.hex()
