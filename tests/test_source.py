import pytest
from pydantic import FileUrl

from ethpm_types.source import Source

SOURCE_LOCATION = (
    "https://github.com/OpenZeppelin/openzeppelin-contracts"
    "/blob/master/contracts/token/ERC20/IERC20.sol"
)
SOURCE_ID = "VyperContract.vy"
SOURCE_CONTENT = """
# @version 0.3.7

import interfaces.IRegistry as IRegistry

registry: public(IRegistry)

@external
def __init__(registry: IRegistry):
    self.registry = registry
""".lstrip()  # Remove \n prefix


@pytest.fixture
def no_checksum() -> Source:
    return Source.parse_obj({"source_id": "Foo.txt", "urls": [SOURCE_LOCATION]})


@pytest.fixture
def bad_checksum() -> Source:
    return Source.parse_obj(
        {
            "source_id": "Foo.txt",
            "urls": [SOURCE_LOCATION],
            "checksum": {"algorithm": "md5", "hash": "0x"},
        }
    )


@pytest.fixture
def empty_source() -> Source:
    return Source.parse_obj({"source_id": "Foo.txt", "content": ""})


@pytest.fixture
def source() -> Source:
    return Source.parse_obj({"source_id": SOURCE_ID, "content": SOURCE_CONTENT})


def test_corrupt_source(bad_checksum, no_checksum):
    assert not no_checksum.content_is_valid()
    assert not bad_checksum.content_is_valid()


def test_empty_source(empty_source):
    assert empty_source.fetch_content() == ""
    assert empty_source.content_is_valid()


def test_source_repr(source):
    # Test default case.
    assert repr(source) == "<Source>"

    # Test that uses file URI when available.
    raw_uri = "file://path/to/file.vy"
    uri = FileUrl(raw_uri, scheme="file")
    source.urls = [uri]
    assert repr(source) == f"<Source {raw_uri}>"

    # Test that favors URI over checksum.
    checksum = source.calculate_checksum()
    source.checksum = checksum
    assert repr(source) == f"<Source {uri}>"

    # Test that uses checksum if available and no URI.
    source.urls = []
    assert repr(source) == f"<Source {checksum.hash}>"


def test_source_line_access(source):
    assert source[0] == "# @version 0.3.7"
    assert source[1] == ""
    assert source[2] == "import interfaces.IRegistry as IRegistry"
    assert source[-1] == "    self.registry = registry"
    assert source[3:5] == ["", "registry: public(IRegistry)"]


def test_enumerate(source):
    for line_idx, line in enumerate(source):
        assert isinstance(line_idx, int)
        assert isinstance(line, str)


def test_len(source):
    assert len(source) == len(SOURCE_CONTENT.splitlines())
