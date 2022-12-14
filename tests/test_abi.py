from ethpm_types.abi import ABIType, ConstructorABI


def test_constructor_selector():
    constructor = ConstructorABI(
        type="constructor",
        inputs=[ABIType(name="contract_address", type="address", internalType="address")],
    )
    assert constructor.selector == "constructor(address)"
