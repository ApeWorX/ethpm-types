import pytest
from hexbytes import HexBytes

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

    @pytest.mark.parametrize("kwarg", ("internal_type", "internalType"))
    def test_internal_type(self, kwarg):
        data = {"name": "_name", "type": "String", "components": None, kwarg: "string"}
        abi_type = ABIType.model_validate(data)
        assert abi_type.internal_type == "string"


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
        assert constructor in {constructor, ConstructorABI()}


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
        assert event in {event, EventABI(name="BarEvent")}

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
        ]
        assert actual == expected

    def test_encode_topics_no_inputs(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 value, uint)"
        event = EventABI.from_signature(signature)
        topics = {}
        actual = event.encode_topics(topics)
        expected = ["0x36a46ac9279f9cc24a2b0ce490d205f822f91eb09330ba01a04d4b20577e469c"]
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

    def test_encode_topics_multiple_values(self):
        event = EventABI(
            type="event",
            name="FooHappened",
            inputs=[
                EventABIType(
                    name="foo",
                    type="uint256",
                    components=None,
                    internal_type="uint256",
                    indexed=True,
                )
            ],
            anonymous=False,
        )
        actual = event.encode_topics({"foo": [0, 1]})
        expected = [
            "0x1a7c56fae0af54ebae73bc4699b9de9835e7bb86b050dff7e80695b633f17abd",
            [
                "0x0000000000000000000000000000000000000000000000000000000000000000",
                "0x0000000000000000000000000000000000000000000000000000000000000001",
            ],
        ]
        assert actual == expected

    def test_encode_topics_dynamic_value(self):
        event = EventABI(
            type="event",
            name="FooHappened",
            inputs=[
                EventABIType(
                    name="fooStr",
                    type="string",
                    components=None,
                    internal_type="string",
                    indexed=True,
                )
            ],
            anonymous=False,
        )
        actual = event.encode_topics({"fooStr": "hello ethpm-types"})
        expected = [
            "0x303e54345675e954e1d04b6cc303625da54125e099e74eaa668ceebb40f49e8a",
            "0x6bd959934a59ba145da1523272e142d1f6f9872a1bc797562e0348fc6aea9a89",
        ]
        assert actual == expected

    def test_encode_topics_multiple_dynamic_values(self):
        event = EventABI(
            type="event",
            name="FooHappened",
            inputs=[
                EventABIType(
                    name="fooStr",
                    type="string",
                    components=None,
                    internal_type="string",
                    indexed=True,
                )
            ],
            anonymous=False,
        )
        actual = event.encode_topics({"fooStr": ["hello ethpm-types", "hello apes"]})
        expected = [
            "0x303e54345675e954e1d04b6cc303625da54125e099e74eaa668ceebb40f49e8a",
            [
                "0x6bd959934a59ba145da1523272e142d1f6f9872a1bc797562e0348fc6aea9a89",
                "0x7569d0c03843b022429ec0c9988a82a58e69908d9df2cd80c1da50bb2aee5239",
            ],
        ]
        assert actual == expected

    def test_encode_topics_removes_trailing_wildcards(self):
        signature = "Transfer(address indexed from, address indexed to, uint256 indexed value)"
        event = EventABI.from_signature(signature)
        actual = event.encode_topics({"from": None, "to": "0x01", "value": None})
        # The first None stays because it is not trailing. The second None is gone because
        # it is for `.value`, which is trailing.
        expected = [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            None,
            "0x0000000000000000000000000000000000000000000000000000000000000001",
        ]
        assert actual == expected

    def test_encode_topics_bytes_for_string(self):
        event = EventABI(
            type="event",
            name="StringBytesEvent",
            inputs=[
                EventABIType(
                    name="dynIndexed",
                    type="string",
                    components=None,
                    internal_type=None,
                    indexed=True,
                ),
            ],
            anonymous=False,
        )
        data = {"dynIndexed": HexBytes(123)}
        actual = event.encode_topics(data)
        expected = [
            "0x6168f6acac733ad1199187f85ee89781c4dfd2e625b4be24d437ec707bd1a82a",
            "0x38848aa0a2dad98b7c8ce946459e3426193e71ee439c7b0ceb2dfb615cf41df9",
        ]
        assert actual == expected

    def test_encode_topics_int_for_string(self):
        event = EventABI(
            type="event",
            name="StringBytesEvent",
            inputs=[
                EventABIType(
                    name="dynIndexed",
                    type="string",
                    components=None,
                    internal_type=None,
                    indexed=True,
                ),
            ],
            anonymous=False,
        )
        data = {"dynIndexed": 123}
        actual = event.encode_topics(data)
        expected = [
            "0x6168f6acac733ad1199187f85ee89781c4dfd2e625b4be24d437ec707bd1a82a",
            "0x38848aa0a2dad98b7c8ce946459e3426193e71ee439c7b0ceb2dfb615cf41df9",
        ]
        assert actual == expected

    # Topics emitted by a solc 0.8.30 contract (`emit Foo(value, 0)`).
    @pytest.mark.parametrize(
        "ipt,value,topic",
        [
            (
                {"type": "uint256[2]"},
                [7, 9],
                "0xae6299332bcd708cd60e3a8defa55de28078a50a4cf2b3de3a546253240ff9e1",
            ),
            (
                {"type": "address[]"},
                [
                    "0x000000000000000000000000000000000000dEaD",
                    "0x000000000000000000000000000000000000bEEF",
                ],
                "0xa0ba882e59c222b5b97e6c80d5ee586dcb6aadfc3ffb7a43e3be291a09fa12e1",
            ),
            (
                {"type": "uint256[][]"},
                [[1], []],
                "0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6",
            ),
            (
                {"type": "string[]"},
                ["a", "", "this string is longer than thirty-two bytes!"],
                "0xff410e4ddf62e0fd3820329c257a13eab6fd5d82a9b2681a4488703f86a45756",
            ),
            (
                {
                    "type": "tuple",
                    "components": [
                        {"name": "a", "type": "uint256"},
                        {"name": "b", "type": "address"},
                    ],
                },
                (5, "0x000000000000000000000000000000000000dEaD"),
                "0x6e34d48e6c189b6316c0dc69278f7052e7faca4f115cf729e597986a65ab6dd0",
            ),
            (
                {
                    "type": "tuple",
                    "components": [
                        {"name": "s", "type": "string"},
                        {"name": "xs", "type": "uint256[]"},
                        {"name": "b", "type": "bytes"},
                    ],
                },
                ("hi", [3, 4], b""),
                "0x40d7f0f88d9c6893f565f67d2a5c6ff462e9f8dafc4945bdcf4686b1f0b8324d",
            ),
        ],
    )
    def test_encode_topics_indexed_reference_types(self, ipt, value, topic):
        event = EventABI(
            name="Foo",
            inputs=[
                EventABIType(name="foo", indexed=True, **ipt),
                EventABIType(name="marker", type="uint256"),
            ],
        )
        actual = event.encode_topics({"foo": value})
        assert actual[1] == topic
        # The topic itself, e.g. a decoded log value, passes through as-is.
        assert event.encode_topics({"foo": HexBytes(topic)})[1] == topic

    def test_encode_topics_multiple_array_values(self):
        event = EventABI.from_signature("Arr(uint256[2] indexed xs, uint256 marker)")
        actual = event.encode_topics({"xs": [[7, 9], [1, 2]]})
        expected = [
            "0x423b48f13db3ea4764a250a9c4c8e23a6c898fe7b9c01b940c086dba08a3597e",
            [
                "0xae6299332bcd708cd60e3a8defa55de28078a50a4cf2b3de3a546253240ff9e1",
                "0xe90b7bceb6e7df5418fb78d8ee546e97c83a08bbccc01a0644d599ccd2a7c2e0",
            ],
        ]
        assert actual == expected

    def test_encode_topics_hashed_string(self):
        event = EventABI.from_signature("Str(string indexed s, uint256 marker)")
        topic = "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"
        assert event.encode_topics({"s": "hello"})[1] == topic
        assert event.encode_topics({"s": HexBytes(topic)})[1] == topic


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
        assert abi in {abi, MethodABI(name="OtherMethod")}

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

    def test_append(self):
        abi1 = MethodABI.from_signature("transfer(address to, uint256 value)")
        abi2 = MethodABI.from_signature("transferFrom(address from, uint256 value)")
        abi3 = MethodABI.from_signature("transferNow(address someone, uint256 value)")
        abi_ls = ABIList((abi1,))
        abi_ls.append(abi2)
        assert len(abi_ls) == 2
        abi_ls.append(abi3)
        assert len(abi_ls) == 3
        assert abi_ls[abi1.selector] == abi1
        assert abi_ls[abi2.selector] == abi2
        assert abi_ls[abi3.selector] == abi3

    def test_extend(self):
        abi1 = MethodABI.from_signature("transfer(address to, uint256 value)")
        abi2 = MethodABI.from_signature("transferFrom(address from, uint256 value)")
        abi3 = MethodABI.from_signature("transferNow(address someone, uint256 value)")
        abi_ls = ABIList((abi1,))
        abi_ls.extend((abi2,))
        assert len(abi_ls) == 2
        abi_ls.extend(ABIList((abi3,)))
        assert len(abi_ls) == 3
        assert abi_ls[abi1.selector] == abi1
        assert abi_ls[abi2.selector] == abi2
        assert abi_ls[abi3.selector] == abi3

    def test_model_validate_str(self):
        abi_str = """
        [
            {
                "type": "function",
                "name": "setAmount",
                "stateMutability": "nonpayable",
                "inputs": [
                    {
                        "name": "newAmount",
                        "type": "uint256",
                        "components": null,
                        "internalType": "uint256"
                    }
                ],
                "outputs": []
            }
        ]
        """.strip()
        abi_ls = ABIList.model_validate(abi_str)
        assert len(abi_ls) == 1
        assert abi_ls[0].name == "setAmount"
        assert abi_ls[0].type == "function"
        assert len(abi_ls[0].inputs) == 1
        assert abi_ls[0].inputs[0].name == "newAmount"
