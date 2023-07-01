from ethpm_types import ContractType

CAIRO_ABI = [
    {
        "type": "struct",
        "name": "MyStruct",
        "members": [
            {"name": "foo", "type": "felt", "offset": 0},
            {"name": "bar", "type": "felt", "offset": 1},
        ],
        "size": 2,
    },
    {"type": "event", "name": "Upgraded", "inputs": [], "anonymous": False},
    {
        "type": "constructor",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "implementation_address", "type": "felt"}],
    },
    {
        "type": "function",
        "name": "compare_arrays",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "a_len", "type": "felt"},
            {"name": "a", "type": "felt*"},
            {"name": "b_len", "type": "felt"},
            {"name": "b", "type": "felt*"},
        ],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "increase_balance",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "amount", "type": "felt"}],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "get_balance",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "res", "type": "felt"}],
    },
    {
        "type": "function",
        "name": "sum_points",
        "stateMutability": "view",
        "inputs": [{"name": "points", "type": "(Point, Point)"}],
        "outputs": [{"name": "res", "type": "Point"}],
    },
    {
        "type": "function",
        "name": "__default__",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "selector", "type": "felt"},
            {"name": "calldata_size", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
        ],
        "outputs": [{"name": "retdata_size", "type": "felt"}, {"name": "retdata", "type": "felt*"}],
    },
    {
        "inputs": [
            {"name": "selector", "type": "felt"},
            {"name": "calldata_size", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
        ],
        "name": "__l1_default__",
        "outputs": [],
        "type": "l1_handler",
    },
]


def test_cairo_abi():
    contract_type = ContractType.parse_obj({"abi": CAIRO_ABI})

    assert len(contract_type.structs) == 1
    assert contract_type.structs[0].name == "MyStruct"
    assert contract_type.structs["MyStruct"].name == "MyStruct"

    abi = contract_type.abi

    # Verify struct
    struct = abi[0]
    raw_struct = struct.dict()
    assert struct.type == raw_struct["type"] == "struct"
    assert struct.size == raw_struct["size"] == 2

    struct_member_0 = struct.members[0]
    raw_struct_member_0 = struct_member_0.dict()
    struct_member_1 = struct.members[1]
    raw_struct_member_1 = struct_member_1.dict()
    assert struct_member_0.name == raw_struct_member_0["name"] == "foo"
    assert struct_member_0.offset == raw_struct_member_0["offset"] == 0
    assert struct_member_1.name == raw_struct_member_1["name"] == "bar"
    assert struct_member_1.offset == raw_struct_member_1["offset"] == 1

    # Verify event
    event = abi[1]
    event_raw = event.dict()
    assert event.name == event_raw["name"] == "Upgraded"

    # Verify constructor
    constructor = abi[2]
    constructor_raw = constructor.dict()
    assert constructor.type == constructor_raw["type"] == "constructor"

    # Verify L1 handler
    l1_handler = abi[-1]
    l1_handler_raw = l1_handler.dict()
    assert l1_handler.type == l1_handler_raw["type"] == "l1_handler"
    assert l1_handler.name == l1_handler_raw["name"] == "__l1_default__"
