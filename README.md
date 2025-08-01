# Quick Start

EthPM is an Ethereum package manifest containing data types for contracts, deployments, and source code using [EIP-2678](https://eips.ethereum.org/EIPS/eip-2678).
The library validates and serializes contract related data and provides JSON schemas.

## Dependencies

- [python3](https://www.python.org/downloads) version 3.9 to 3.12.

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ethpm-types
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ethpm-types.git
cd ethpm-types
python3 setup.py install
```

## Quick Usage

Starting with a dictionary of attribute data, such as a contract instance, you can build an EthPM typed object.

```python
from ethpm_types import ContractInstance

contract = ContractInstance(contractType="ContractClassName", address="0x123...")
print(contract.contract_type)
```

### Contract Type

Perhaps the most common artifact type from `ethmp_types` is `ContractType`.
`ContractType` represents components of a compiled contract, such as the `.abi` or the `.runtime_bytecode`.

```python
from ethpm_types import ContractType

contract = ContractType(abi=[], runtimeBytecode="0x...")
```

For convenience, you can also initialize a `ContractType` using the `.from_signature()` classmethod:

```python
from ethpm_types.abi import MethodABI, EventABI

MethodABI.from_signature("function_name(uint256 arg1)")
# => MethodABI(type='function', name='function_name', inputs=[...], ...)

EventABI.from_signature("Transfer(address indexed from, address indexed to, uint256 value)")
# => EventABI(type='event', name='Transfer', inputs=[...], ...)
```

#### ABI JSON

To easily acquire the ABI JSON for a `ContractType` artifact, `.model_dump_json()` the `.abi` property:

```python
from ethpm_types import ContractType

contract_type = ContractType(abi=[], runtimeBytecode="0x...")

# Use the ABI in other application requiring ABI JSON.
abi = contract_type.abi.model_dump_json()
```
