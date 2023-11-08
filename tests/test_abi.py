from ethpm_types.abi import ABIType, ConstructorABI, ReceiveABI


def test_abitype_schema():
    actual = ABIType.schema()
    expected = {
        "$ref": "#/definitions/ABIType",
        "definitions": {
            "ABIType": {
                "properties": {
                    "components": {
                        "items": {"$ref": "#/definitions/ABIType"},
                        "title": "Components",
                        "type": "array",
                    },
                    "internalType": {"title": "Internaltype", "type": "string"},
                    "name": {"title": "Name", "type": "string"},
                    "type": {
                        "anyOf": [{"type": "string"}, {"$ref": "#/definitions/ABIType"}],
                        "title": "Type",
                    },
                },
                "required": ["type"],
                "title": "ABIType",
                "type": "object",
            }
        },
    }
    assert actual == expected


def test_constructor_abi_schema():
    actual = ConstructorABI.schema()
    assert actual["$ref"] == "#/definitions/ConstructorABI"
    assert "ABIType" in actual["definitions"]

    # contract_type backrefs MUST be internal constructs
    # for FastAPI integration to work properly.
    assert "ContractType" not in actual["definitions"]


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
