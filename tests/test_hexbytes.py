from ethpm_types import BaseModel, HexBytes

TEST_MODEL_DICT = {
    "byte_bytes": b"\x00",
    "bytearray_bytes": bytearray([0]),
    "str_bytes": "0x0",
    "int_bytes": 0,
    "bool_bytes": False,
}


class TestModel(BaseModel):
    byte_bytes: HexBytes
    bytearray_bytes: HexBytes
    str_bytes: HexBytes
    int_bytes: HexBytes
    bool_bytes: HexBytes


def test_hexbytes_dict():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)
    test_dict = test_model.dict()
    assert len(test_dict) == 5

    for _, v in test_dict.items():
        assert v == "0x00"


def test_hexbytes_dict_exclude():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)

    test_dict = test_model.dict(exclude={"byte_bytes"})
    assert len(test_dict) == 4
    assert "byte_bytes" not in test_dict.keys()


def test_hexbytes_json():
    test_model = TestModel.parse_obj(TEST_MODEL_DICT)
    test_json = test_model.json(exclude={"bool_bytes", "byte_bytes", "int_bytes"})

    assert test_json == '{"bytearray_bytes":"0x00","str_bytes":"0x00"}'
