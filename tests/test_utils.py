from ethpm_types import EventABI
from ethpm_types.abi import EventABIType
from ethpm_types.utils import compute_checksum, parse_signature


def test_compute_checksum():
    content = b"this is content"
    actual = compute_checksum(content)
    assert actual.startswith("0x")


def test_parse_signature():
    event = EventABI(name="FooEvent")
    signature = event.signature
    actual = parse_signature(signature)
    assert actual == ("FooEvent", [], [])


def test_parse_signature_anonymous_input():
    ipt = EventABIType(name=None, type="uint256")
    event = EventABI(name="FooEvent", inputs=[ipt])
    signature = event.signature
    actual = parse_signature(signature)
    expected_inputs = [("uint256", "", "")]
    assert actual == ("FooEvent", expected_inputs, [])


def test_parse_signature_named_input():
    ipt = EventABIType(name="bar", type="uint256")
    event = EventABI(name="FooEvent", inputs=[ipt])
    signature = event.signature
    actual = parse_signature(signature)
    expected_inputs = [("uint256", "", "bar")]
    assert actual == ("FooEvent", expected_inputs, [])


def test_parse_signature_indexed_input():
    ipt = EventABIType(name="bar", type="uint256", indexed=True)
    event = EventABI(name="FooEvent", inputs=[ipt])
    signature = event.signature
    actual = parse_signature(signature)
    expected_inputs = [("uint256", "indexed", "bar")]
    assert actual == ("FooEvent", expected_inputs, [])


def test_parse_signature_tuple_inputs():
    ipt = EventABIType(type="(uint256,address)")
    event = EventABI(name="FooEvent", inputs=[ipt])
    signature = event.signature
    actual = parse_signature(signature)
    expected_inputs = [("(uint256,address)", "", "")]
    assert actual == ("FooEvent", expected_inputs, [])


def test_parse_signature_indexed_and_named_tuple_inputs():
    ipt = EventABIType(type="(uint256,address)", name="bartup", indexed=True)
    event = EventABI(name="FooEvent", inputs=[ipt])
    signature = event.signature
    actual = parse_signature(signature)
    expected_inputs = [("(uint256,address)", "indexed", "bartup")]
    assert actual == ("FooEvent", expected_inputs, [])


def test_parse_signature_multiple_inputs():
    signature = "Transfer(address indexed from, address indexed to, uint256 value)"
    actual = parse_signature(signature)
    expected = (
        "Transfer",
        [("address", "indexed", "from"), ("address", "indexed", "to"), ("uint256", "", "value")],
        [],
    )
    assert actual == expected
