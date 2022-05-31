import json
from pathlib import Path

from ethpm_types.contract_type import Bytecode


def test_bytecode():
    path = Path(__file__).parent / "data" / "Bytecode.json"
    data = json.loads(path.read_text())
    hex_bin = Bytecode.parse_obj(data)
    assert hex_bin.bytecode
