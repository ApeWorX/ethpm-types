from ethpm_types import EventABI
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
