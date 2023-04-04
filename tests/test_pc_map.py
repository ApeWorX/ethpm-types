from ethpm_types.sourcemap import PCMap, PCMapItem


def test_pc_map_valid():
    """
    Test the parsing of a valid pc-map from a compiler's output.
    """
    pcmap = PCMap.parse_obj({"186": [10, 20, 10, 40]}).parse()

    keys = list(pcmap.keys())

    assert len(keys) == 1
    assert keys[0] == 186
    assert pcmap[186] == PCMapItem(line_start=10, column_start=20, line_end=10, column_end=40)


def test_pc_map_empty_line_info():
    """
    Test the parsing of a pc-map from a compiler's output that has empty line
    information.
    """
    pcmap = PCMap.parse_obj({"186": [None, None, None, None]}).parse()

    keys = list(pcmap.keys())

    assert len(keys) == 1
    assert keys[0] == 186
    assert pcmap[186] == PCMapItem(
        line_start=None, column_start=None, line_end=None, column_end=None
    )


def test_pc_map_missing_line_info():
    """
    Test the parsing of a pc-map from a compiler's output that is entirely missing line
    information.
    """
    pcmap = PCMap.parse_obj({"186": None}).parse()

    keys = list(pcmap.keys())

    assert len(keys) == 1
    assert keys[0] == 186
    assert pcmap[186] == PCMapItem(
        line_start=None, column_start=None, line_end=None, column_end=None
    )


def test_pc_map_empty():
    """
    Test the parsing of an empty pc-map from a compiler's output.
    """
    pcmap = PCMap.parse_obj({}).parse()

    assert pcmap == {}


def test_pc_map_getting_and_setting():
    pcmap = PCMap.parse_obj({"186": [10, 20, 10, 40]})

    # Test __contains__
    assert "186" in pcmap
    assert 186 in pcmap

    # Test __getitem__
    assert pcmap[186] == {"location": [10, 20, 10, 40]}
    assert pcmap["186"] == {"location": [10, 20, 10, 40]}

    # Test __setitem__
    pcmap[184] = [5, 20, 10, 40]
    assert pcmap["184"] == {"location": [5, 20, 10, 40]}
