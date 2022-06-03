from hexbytes import HexBytes as OriginalHexBytes

from ethpm_types import BaseModel, HexBytes

TEST_MODEL_DICT = {
    "byte_bytes": b"\x00",
    "bytearray_bytes": bytearray([0]),
    "str_bytes": "0x0",
    "int_bytes": 0,
    "bool_bytes": False,
    "original_bytes": OriginalHexBytes("0"),
}


class TestModel(BaseModel):
    byte_bytes: HexBytes
    bytearray_bytes: HexBytes
    str_bytes: HexBytes
    int_bytes: HexBytes
    bool_bytes: HexBytes
    original_bytes: HexBytes


def test_hexbytes_dict():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)

    for _, item in test_model.__fields__.items():
        assert item.type_ == HexBytes

    test_dict = test_model.dict()
    assert len(test_dict) == 6

    for _, v in test_dict.items():
        assert v == "0x00"


def test_hexbytes_dict_exclude():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)

    test_dict = test_model.dict(exclude={"byte_bytes"})
    assert len(test_dict) == 5
    assert "byte_bytes" not in test_dict.keys()


def test_hexbytes_json():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)
    test_json = test_model.json(exclude={"bool_bytes", "byte_bytes", "int_bytes"})

    assert test_json == '{"bytearray_bytes":"0x00","original_bytes":"0x00","str_bytes":"0x00"}'
