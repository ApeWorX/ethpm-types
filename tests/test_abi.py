import pytest

from ethpm_types.abi import (
    ABIType,
    ConstructorABI,
    EventABI,
    EventABIType,
    FallbackABI,
    MethodABI,
    ReceiveABI,
    UnprocessedABI,
)


class TestABIType:
    def test_canonical_type_when_string(self):
        abi = ABIType(name="foo", type="string")
        assert abi.canonical_type == "string"

    def test_canonical_type_when_tuple(self):
        abi = ABIType(name="foo", type="tuple", components=[ABIType(name="bar", type="string")])
        assert abi.canonical_type == "(string)"

    def test_schema(self):
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


class TestConstructorABI:
    def test_schema(self):
        actual = ConstructorABI.schema()
        assert actual["$ref"] == "#/definitions/ConstructorABI"
        assert len(actual["definitions"]) == 2
        assert ABIType.__name__ in actual["definitions"]
        assert ConstructorABI.__name__ in actual["definitions"]

    def test_selector(self):
        constructor = ConstructorABI(
            inputs=[ABIType(name="contract_address", type="address", internalType="address")],
        )
        assert constructor.selector == "constructor(address)"


class TestEventABI:
    def test_schema(self):
        actual = EventABI.schema()
        assert actual["$ref"] == "#/definitions/EventABI"
        assert len(actual["definitions"]) == 3
        assert ABIType.__name__ in actual["definitions"]
        assert EventABIType.__name__ in actual["definitions"]
        assert EventABI.__name__ in actual["definitions"]

    def test_selector(self):
        event = EventABI(name="FooEvent")
        assert event.selector == "FooEvent()"


class TestFallbackABI:
    @pytest.mark.parametrize(
        "state_mutability,expected", [("payable", True), ("nonpayable", False)]
    )
    def test_is_payable(self, state_mutability, expected):
        abi = FallbackABI(stateMutability=state_mutability)
        assert abi.is_payable == expected

    def test_schema(self):
        actual = FallbackABI.schema()
        assert actual["$ref"] == "#/definitions/FallbackABI"
        assert len(actual["definitions"]) == 2
        assert ABIType.__name__ in actual["definitions"]
        assert FallbackABI.__name__ in actual["definitions"]


class TestMethodABI:
    def test_schema(self):
        actual = MethodABI.schema()
        assert actual["$ref"] == "#/definitions/MethodABI"
        assert len(actual["definitions"]) == 2
        assert ABIType.__name__ in actual["definitions"]
        assert MethodABI.__name__ in actual["definitions"]

    def test_selector(self):
        abi = MethodABI(
            name="MyMethod",
            inputs=[
                ABIType(name="foo", type="address"),
                ABIType(name="bar", type="string"),
            ],
        )
        assert abi.selector == "MyMethod(address,string)"


class TestReceiveABI:
    def test_properties(self):
        receive = ReceiveABI(stateMutability="payable")
        assert receive.type == "receive"
        assert receive.stateMutability == "payable"

    def test_schema(self):
        actual = ReceiveABI.schema()
        assert actual["$ref"] == "#/definitions/ReceiveABI"
        assert len(actual["definitions"]) == 2
        assert ABIType.__name__ in actual["definitions"]
        assert ReceiveABI.__name__ in actual["definitions"]


class TestUnprocessedABI:
    def test_schema(self):
        actual = UnprocessedABI.schema()
        assert actual["$ref"] == "#/definitions/UnprocessedABI"
        assert len(actual["definitions"]) == 2
        assert ABIType.__name__ in actual["definitions"]
        assert UnprocessedABI.__name__ in actual["definitions"]
