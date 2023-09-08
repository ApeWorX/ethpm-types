from typing import Dict, List, Optional

from hexbytes import HexBytes as OriginalHexBytes

from ethpm_types import BaseModel, HexBytes
from ethpm_types._pydantic_v1 import Field

TEST_MODEL_DICT = {
    "byte_bytes": b"\x00",
    "bytearray_bytes": bytearray([0]),
    "str_bytes": "0x0",
    "int_bytes": 0,
    "bool_bytes": False,
    "original_bytes": OriginalHexBytes("0"),
    "optional_bytes": HexBytes(0),
}
EMPTY_BYTES = HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")


class TestModel(BaseModel):
    byte_bytes: HexBytes
    bytearray_bytes: HexBytes
    str_bytes: HexBytes
    int_bytes: HexBytes
    bool_bytes: HexBytes
    original_bytes: HexBytes
    optional_bytes: Optional[HexBytes] = None


class Block(BaseModel):
    gas_limit: int = Field(alias="gasLimit")
    hash: Optional[HexBytes] = None
    parent_hash: HexBytes = Field(EMPTY_BYTES, alias="parentHash")


def test_hexbytes_dict():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)

    for _, item in test_model.__fields__.items():
        assert item.type_ == HexBytes

    test_dict = test_model.dict()
    assert len(test_dict) == 7

    for _, v in test_dict.items():
        assert v == "0x00"


def test_hexbytes_dict_exclude():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)

    test_dict = test_model.dict(exclude={"byte_bytes"})
    assert len(test_dict) == 6
    assert "byte_bytes" not in test_dict.keys()


def test_hexbytes_json():
    test_models = (TestModel.parse_obj(TEST_MODEL_DICT), TestModel(**TEST_MODEL_DICT))
    for model in test_models:
        test_json = model.json(exclude={"bool_bytes", "byte_bytes", "int_bytes"})
        assert test_json == (
            '{"bytearray_bytes":"0x00",'
            '"optional_bytes":"0x00",'
            '"original_bytes":"0x00",'
            '"str_bytes":"0x00"}'
        )


def test_realistic_model():
    block = Block(
        gasLimit=123124,
        hash=HexBytes("0x1be99d96b0b5784b07aea2750aee16a2efbe46cf271b246835bc101fd94bc992"),
    )
    actual = block.json(sort_keys=True)
    expected = (
        '{"gasLimit":123124,'
        '"hash":"0x1be99d96b0b5784b07aea2750aee16a2efbe46cf271b246835bc101fd94bc992",'
        f'"parentHash":"{EMPTY_BYTES.hex()}"}}'
    )
    assert actual == expected


def test_hexbytes_as_key():
    """
    Tests against a condition where we could not use
    HexBytes as keys. Sometimes, this is needed such as
    in low-level objects such as struct logs.
    """

    class Model(BaseModel):
        key: HexBytes  # type: ignore[annotation-unchecked]
        keys: List[HexBytes]  # type: ignore[annotation-unchecked]
        sub_dict: Dict[HexBytes, HexBytes]  # type: ignore[annotation-unchecked]

    sub_dict = {HexBytes(3): HexBytes(4)}
    model = Model(key=HexBytes(1), keys=[HexBytes(2)], sub_dict=sub_dict)
    actual = model.json()
    assert isinstance(actual, str)
