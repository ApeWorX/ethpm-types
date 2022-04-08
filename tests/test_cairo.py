from ethpm_types import ContractType

CAIRO_ERC20_ABI = [
    {
        "members": [
            {"name": "low", "offset": 0, "type": "felt"},
            {"name": "high", "offset": 1, "type": "felt"},
        ],
        "name": "Uint256",
        "size": 2,
        "type": "struct",
    },
    {
        "inputs": [
            {"name": "name", "type": "felt"},
            {"name": "symbol", "type": "felt"},
            {"name": "recipient", "type": "felt"},
        ],
        "name": "constructor",
        "outputs": [],
        "type": "constructor",
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "name", "type": "felt"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "symbol", "type": "felt"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "totalSupply", "type": "Uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "decimals", "type": "felt"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "felt"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "Uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "owner", "type": "felt"}, {"name": "spender", "type": "felt"}],
        "name": "allowance",
        "outputs": [{"name": "remaining", "type": "Uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "recipient", "type": "felt"}, {"name": "amount", "type": "Uint256"}],
        "name": "transfer",
        "outputs": [{"name": "success", "type": "felt"}],
        "type": "function",
    },
    {
        "inputs": [
            {"name": "sender", "type": "felt"},
            {"name": "recipient", "type": "felt"},
            {"name": "amount", "type": "Uint256"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "success", "type": "felt"}],
        "type": "function",
    },
    {
        "inputs": [{"name": "spender", "type": "felt"}, {"name": "amount", "type": "Uint256"}],
        "name": "approve",
        "outputs": [{"name": "success", "type": "felt"}],
        "type": "function",
    },
    {
        "inputs": [{"name": "spender", "type": "felt"}, {"name": "added_value", "type": "Uint256"}],
        "name": "increaseAllowance",
        "outputs": [{"name": "success", "type": "felt"}],
        "type": "function",
    },
    {
        "inputs": [
            {"name": "spender", "type": "felt"},
            {"name": "subtracted_value", "type": "Uint256"},
        ],
        "name": "decreaseAllowance",
        "outputs": [{"name": "success", "type": "felt"}],
        "type": "function",
    },
    {
        "inputs": [{"name": "recipient", "type": "felt"}, {"name": "amount", "type": "Uint256"}],
        "name": "mint",
        "outputs": [],
        "type": "function",
    },
    {
        "inputs": [{"name": "user", "type": "felt"}, {"name": "amount", "type": "Uint256"}],
        "name": "burn",
        "outputs": [],
        "type": "function",
    },
]


def test_cairo_abi():
    contract_type = ContractType.parse_obj({"abi": CAIRO_ERC20_ABI})
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
    assert struct_member_0.name == raw_struct_member_0["name"] == "low"
    assert struct_member_0.offset == raw_struct_member_0["offset"] == 0
    assert struct_member_1.name == raw_struct_member_1["name"] == "high"
    assert struct_member_1.offset == raw_struct_member_1["offset"] == 1

    # Verify constructor
    constructor = abi[1]
    constructor_raw = constructor.dict()
    assert constructor.type == constructor_raw["type"] == "constructor"
