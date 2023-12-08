from ethpm_types.utils import compute_checksum


def test_compute_checksum():
    content = "this is content".encode("utf8")
    actual = compute_checksum(content)
    assert actual.startswith("0x")
