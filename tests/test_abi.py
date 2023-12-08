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
        actual = ABIType.model_json_schema()
        expected = {
            "$defs": {
                "ABIType": {
                    "additionalProperties": True,
                    "properties": {
                        "name": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Name",
                        },
                        "type": {
                            "anyOf": [{"type": "string"}, {"$ref": "#/$defs/ABIType"}],
                            "title": "Type",
                        },
                        "components": {
                            "anyOf": [
                                {"items": {"$ref": "#/$defs/ABIType"}, "type": "array"},
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Components",
                        },
                        "internalType": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Internaltype",
                        },
                    },
                    "required": ["type"],
                    "title": "ABIType",
                    "type": "object",
                }
            },
            "allOf": [{"$ref": "#/$defs/ABIType"}],
        }
        assert actual == expected


class TestConstructorABI:
    def test_schema(self):
        actual = ConstructorABI.model_json_schema()
        assert len(actual["$defs"]) == 1
        assert ABIType.__name__ in actual["$defs"]
        assert ConstructorABI.__name__ in actual["title"]

    def test_selector(self):
        constructor = ConstructorABI(
            inputs=[ABIType(name="contract_address", type="address", internalType="address")],
        )
        assert constructor.selector == "constructor(address)"


class TestEventABI:
    def test_schema(self):
        actual = EventABI.model_json_schema()
        assert len(actual["$defs"]) == 2
        assert ABIType.__name__ in actual["$defs"]
        assert EventABIType.__name__ in actual["$defs"]
        assert EventABI.__name__ in actual["title"]

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
        actual = FallbackABI.model_json_schema()
        assert not hasattr(actual, "$defs")
        assert FallbackABI.__name__ in actual["title"]


class TestMethodABI:
    def test_schema(self):
        actual = MethodABI.model_json_schema()
        assert len(actual["$defs"]) == 1
        assert ABIType.__name__ in actual["$defs"]
        assert MethodABI.__name__ in actual["title"]

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
        actual = ReceiveABI.model_json_schema()
        assert not hasattr(actual, "$defs")
        assert ReceiveABI.__name__ in actual["title"]


class TestUnprocessedABI:
    def test_schema(self):
        actual = UnprocessedABI.model_json_schema()
        assert not hasattr(actual, "$defs")
        assert UnprocessedABI.__name__ in actual["title"]
