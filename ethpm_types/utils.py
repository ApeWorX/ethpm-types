from hashlib import md5
from typing import Type

from eth_utils import to_bytes, to_hex


class Bytes32(bytes):
    """
    Custom bytes wrapper class for working with pydantic models.
    Converts str to bytes with a length of 32 and serializes as hex.
    Inspired by HexBytes https://github.com/ethereum/hexbytes/blob/master/hexbytes/main.py
    """

    bytes_length: int = 32

    def __new__(cls: Type[bytes], val: str):
        val = to_bytes(hexstr=val)
        if len(val) != Bytes32.bytes_length:
            return ValueError(f"Value length should be {Bytes32.bytes_length} not '{len(val)}'.")
        return super().__new__(cls, val)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    def validate(cls, v):
        v = to_bytes(hexstr=v)
        if len(v) != Bytes32.bytes_length:
            return ValueError(f"Value length should be 32 not '{len(v)}'.")
        return v

    @staticmethod
    def __serialize__(v: bytes):
        return to_hex(v)

    def __str__(self) -> str:
        return to_hex(self)


def compute_checksum(source: bytes, algorithm: str = "md5") -> str:
    if algorithm == "md5":
        hasher = md5
    else:
        raise Exception("Unknown algorithm")

    return hasher(source).hexdigest()


def is_valid_hash(data: str) -> bool:
    if set(data.lower()) > set("1234567890abcdef"):
        return False

    if len(data) % 2 != 0:
        return False

    return True
