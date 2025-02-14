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
from ethpm_types.contract_type import ABIList


class TestABIType:
    def test_canonical_type_when_string(self):
        abi = ABIType(name="foo", type="string")
        assert abi.canonical_type == "string"

    def test_canonical_type_when_tuple(self):
        abi = ABIType(name="foo", type="tuple", components=[ABIType(name="bar", type="string")])
        assert abi.canonical_type == "(string)"

    def test_model_dump(self):
        abi = ABIType(name="foo", type="string", internalType="string")
        actual = abi.model_dump()
        assert actual["internalType"] == "string"

    def test_dict(self):
        abi = ABIType(name="foo", type="string", internalType="string")
        actual = abi.dict()
        assert actual["internalType"] == "string"

    def test_model_dump_json(self):
        abi = ABIType(name="foo", type="string", internalType="string")
        actual = abi.model_dump_json()
        assert "internalType" in actual

    def test_json(self):
        abi = ABIType(name="foo", type="string", internalType="string")
        actual = abi.json()
        assert "internalType" in actual

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
            "$ref": "#/$defs/ABIType",
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

    def test_from_signature(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 value)"
        event = EventABI.from_signature(signature)
        assert event.name == "Transfer"
        assert event.signature == signature
        assert event.inputs[0].name == "from"
        assert event.inputs[0].indexed
        assert event.inputs[0].type == "address"
        assert event.inputs[1].name == "to"
        assert event.inputs[1].indexed
        assert event.inputs[1].type == "address"
        assert event.inputs[2].name == "value"
        assert event.inputs[2].indexed is False
        assert event.inputs[2].type == "uint256"

    def test_from_signature_with_nameless_param(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 value, uint)"
        event = EventABI.from_signature(signature)
        assert event.name == "Transfer"
        assert event.signature == signature
        assert event.inputs[0].name == "from"
        assert event.inputs[0].indexed
        assert event.inputs[0].type == "address"
        assert event.inputs[1].name == "to"
        assert event.inputs[1].indexed
        assert event.inputs[1].type == "address"
        assert event.inputs[2].name == "value"
        assert event.inputs[2].indexed is False
        assert event.inputs[2].type == "uint256"
        assert event.inputs[3].name == ""
        assert event.inputs[3].indexed is False
        assert event.inputs[3].type == "uint"

    @pytest.mark.parametrize(
        "sig",
        [
            "Transfer(address indexed from, address indexed to, uint256 value)",
            "Approval(address indexed owner, address indexed spender, uint256 value)",
            "Paused()",
            "NotIndexed(uint256 a, uint8 b)",
        ],
    )
    def test_signature_serialization(self, sig):
        event = EventABI.from_signature(sig)
        assert event.signature == sig

    def test_encode_topics(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 value, uint)"
        event = EventABI.from_signature(signature)
        topics = {
            "from": "0xc627dafb1c8c8f28fbbb560ff4d3c85f602d4a69",
            "to": "0xc627dafb1c8c8f28fbbb560ff4d3c85f602d4a69",
        }
        actual = event.encode_topics(topics)
        expected = [
            "0x36a46ac9279f9cc24a2b0ce490d205f822f91eb09330ba01a04d4b20577e469c",
            "0x000000000000000000000000c627dafb1c8c8f28fbbb560ff4d3c85f602d4a69",
            "0x000000000000000000000000c627dafb1c8c8f28fbbb560ff4d3c85f602d4a69",
        ]
        assert actual == expected

    def test_encode_topics_single_input(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 value, uint)"
        event = EventABI.from_signature(signature)
        topics = {"from": "0xc627dafb1c8c8f28fbbb560ff4d3c85f602d4a69"}
        actual = event.encode_topics(topics)
        expected = [
            "0x36a46ac9279f9cc24a2b0ce490d205f822f91eb09330ba01a04d4b20577e469c",
            "0x000000000000000000000000c627dafb1c8c8f28fbbb560ff4d3c85f602d4a69",
            None,
        ]
        assert actual == expected

    def test_encode_topics_no_inputs(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 value, uint)"
        event = EventABI.from_signature(signature)
        topics = {}
        actual = event.encode_topics(topics)
        expected = [
            "0x36a46ac9279f9cc24a2b0ce490d205f822f91eb09330ba01a04d4b20577e469c",
            None,
            None,
        ]
        assert actual == expected

    def test_encode_topics_int(self):
        signature = "Transfer(int256 indexed value)"
        event = EventABI.from_signature(signature)
        actual = event.encode_topics({"value": 1})
        expected = [
            "0xdfe7b17d34477d236495b6b3e918bcf8a53ae88d483b608ed1daf09f5424b4eb",
            "0x0000000000000000000000000000000000000000000000000000000000000001",
        ]
        assert actual == expected


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

    def test_from_signature(self):
        signature = "transfer(address to, uint256 value)"
        method = MethodABI.from_signature(signature)
        assert method.name == "transfer"
        assert method.signature == signature
        assert method.inputs[0].name == "to"
        assert method.inputs[0].type == "address"
        assert method.inputs[1].name == "value"
        assert method.inputs[1].type == "uint256"

    @pytest.mark.parametrize(
        "sig",
        [
            "transfer(address to, uint256 value)",
            "allowance(address owner, address spender) -> uint256",
            "totalSupply() -> uint256",
            "things() -> (uint256, uint8)",
            "swap(uint8 a, uint256 b) -> (uint256, uint8)",
        ],
    )
    def test_signature_serialization(self, sig):
        method = MethodABI.from_signature(sig)
        assert method.signature == sig


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


class TestABIList:
    def test_get(self):
        signature = "transfer(address to, uint256 value)"
        method_abi = MethodABI.from_signature(signature)
        abi_ls = ABIList((method_abi,))
        # Show the .get() method works.
        actual = abi_ls.get("transfer")
        assert actual.signature == signature
