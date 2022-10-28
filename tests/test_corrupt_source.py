import pytest

from ethpm_types.source import Source

SOURCE_LOCATION = (
    "https://github.com/OpenZeppelin/openzeppelin-contracts"
    "/blob/master/contracts/token/ERC20/IERC20.sol"
)


@pytest.fixture
def no_checksum() -> Source:
    return Source.parse_obj({"urls": [SOURCE_LOCATION]})


@pytest.fixture
def bad_checksum() -> Source:
    return Source.parse_obj(
        {"urls": [SOURCE_LOCATION], "checksum": {"algorithm": "md5", "hash": "0x"}}
    )


@pytest.fixture
def empty_source() -> Source:
    return Source.parse_obj({"content": ""})


def test_corrupt_source(bad_checksum, no_checksum):
    assert not no_checksum.content_is_valid()
    assert not bad_checksum.content_is_valid()


def test_empty_source(empty_source):
    assert empty_source.fetch_content() == ""
    assert empty_source.content_is_valid()
