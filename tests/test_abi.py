from ethpm_types.abi import ABIType, ConstructorABI, ReceiveABI


def test_constructor_selector():
    constructor = ConstructorABI(
        type="constructor",
        inputs=[ABIType(name="contract_address", type="address", internalType="address")],
    )
    assert constructor.selector == "constructor(address)"


def test_receive():
    receive = ReceiveABI(type="receive", stateMutability="payable")
    assert receive.type == "receive"
    assert receive.stateMutability == "payable"
