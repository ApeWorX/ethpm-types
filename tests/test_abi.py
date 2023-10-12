from ethpm_types.abi import ABIType, ConstructorABI, ReceiveABI


def test_abi_type_schema():
    """
    Show that it handles recursive schemas.
    NOTE: This didn't work in Pydantic 2.3 but was fixed in 2.4.2.
    """
    actual = ABIType.model_json_schema()
    definition = actual["$defs"]["ABIType"]
    components = definition["properties"]["components"]
    assert components["anyOf"] == [
        {"items": {"$ref": "#/$defs/ABIType"}, "type": "array"},
        {"type": "null"},
    ]


def test_constructor_selector():
    constructor = ConstructorABI(
        type="constructor",
        inputs=[ABIType(name="contract_address", type="address", internalType="address")],
    )
    assert constructor.selector == "constructor(address)"


def test_receive():
    receive = ReceiveABI(type="receive", stateMutability="payable")
    assert receive.type == "receive"
    assert receive.stateMutability == "payable"
