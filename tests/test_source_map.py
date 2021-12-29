from pathlib import Path
from typing import Iterator

import pytest

from ethpm_types.contract_type import SourceMap, SourceMapItem

SOURCE_MAP_FILES = {p.stem: p for p in sorted(Path("tests/data").glob("*.srcmap"))}


def serialize(sourcemap: Iterator[SourceMapItem]) -> str:
    result = ""
    previous_item = None
    for item in sourcemap:
        if item == previous_item:
            result += ";"
            continue

        skip_start = previous_item and item.start == previous_item.start
        skip_stop = previous_item and item.stop == previous_item.stop
        skip_contract_id = previous_item and item.contract_id == previous_item.contract_id
        skip_jump_code = previous_item and item.jump_code == previous_item.jump_code

        if skip_jump_code and skip_contract_id and skip_stop and skip_start:
            result += ";"

        elif skip_jump_code and skip_contract_id and skip_stop:
            result += str(item.start) if item.start is not None else "-1"
            result += ";"

        elif skip_jump_code and skip_contract_id:
            if not skip_start:
                result += str(item.start) if item.start is not None else "-1"
            result += ":"
            result += str(item.stop) if item.stop is not None else "-1"
            result += ";"

        elif skip_jump_code:
            if not skip_start:
                result += str(item.start) if item.start is not None else "-1"
            result += ":"
            if not skip_stop:
                result += str(item.stop) if item.stop is not None else "-1"
            result += ":"
            result += str(item.contract_id) if item.contract_id is not None else "-1"
            result += ";"

        else:
            if not skip_start:
                result += str(item.start) if item.start is not None else "-1"
            result += ":"
            if not skip_stop:
                result += str(item.stop) if item.stop is not None else "-1"
            result += ":"
            if not skip_contract_id:
                result += str(item.contract_id) if item.contract_id is not None else "-1"
            result += ":"
            result += item.jump_code
            result += ";"

        previous_item = item

    return result[:-1]  # Ignore last ";" char


@pytest.mark.parametrize("sourcemap_filename", SOURCE_MAP_FILES)
def test_source_map(sourcemap_filename):
    sourcemap = SOURCE_MAP_FILES[sourcemap_filename].read_text().strip()
    sm = SourceMap.construct(__root__=sourcemap)
    # Serialize back to the sourcemap to make sure we decoded it properly
    assert serialize(sm.parse()) == sourcemap
