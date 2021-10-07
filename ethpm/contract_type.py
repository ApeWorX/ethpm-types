from typing import List, Optional, Set

from .abi import ABI
from .base import BaseModel
from .utils import is_valid_hash


# TODO link references & link values are for solidity, not used with Vyper
# Offsets are for dynamic links, e.g. EIP1167 proxy forwarder
class LinkDependency(BaseModel):
    offsets: List[int]
    type: str
    value: str


class LinkReference(BaseModel):
    offsets: List[int]
    length: int
    name: Optional[str] = None


class Bytecode(BaseModel):
    bytecode: Optional[str] = None
    linkReferences: Optional[List[LinkReference]] = None
    linkDependencies: Optional[List[LinkDependency]] = None

    def __repr__(self) -> str:
        self_str = super().__repr__()

        # Truncate bytecode for display
        if self.bytecode and len(self.bytecode) > 10:
            self_str = self_str.replace(
                self.bytecode, self.bytecode[:5] + "..." + self.bytecode[-3:]
            )

        return self_str


class ContractInstance(BaseModel):
    contractType: str
    address: str
    transaction: Optional[str] = None
    block: Optional[str] = None
    runtimeBytecode: Optional[Bytecode] = None


class ContractType(BaseModel):
    _keep_fields_: Set[str] = {"abi"}
    _skip_fields_: Set[str] = {"contractName"}
    contractName: str
    sourceId: Optional[str] = None
    deploymentBytecode: Optional[Bytecode] = None
    runtimeBytecode: Optional[Bytecode] = None
    # abi, userdoc and devdoc must conform to spec
    abi: List[ABI] = []
    userdoc: Optional[str] = None
    devdoc: Optional[str] = None

    @property
    def constructor(self) -> Optional[ABI]:
        for abi in self.abi:
            if abi.type == "constructor":
                return abi

        return None

    @property
    def fallback(self) -> Optional[ABI]:
        for abi in self.abi:
            if abi.type == "fallback":
                return abi

        return None

    @property
    def events(self) -> List[ABI]:
        return [abi for abi in self.abi if abi.type == "event"]

    @property
    def calls(self) -> List[ABI]:
        return [abi for abi in self.abi if abi.type == "function" and not abi.is_stateful]

    @property
    def transactions(self) -> List[ABI]:
        return [abi for abi in self.abi if abi.type == "function" and abi.is_stateful]


class BIP122_URI(str):
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern="^blockchain://[0-9a-f]{64}/block/[0-9a-f]{64}$",
            examples=[
                "blockchain://d4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3"
                "/block/752820c0ad7abc1200f9ad42c4adc6fbb4bd44b5bed4667990e64565102c1ba6",
            ],
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_uri
        yield cls.validate_genesis_hash

    @classmethod
    def validate_uri(cls, uri):
        assert uri.startswith("blockchain://"), "Must use 'blockchain' protocol"
        assert (
            len(uri.replace("blockchain://", "").split("/")) == 3
        ), "must be referenced via <genesis_hash>/block/<block_hash>"
        _, block_keyword, _ = uri.replace("blockchain://", "").split("/")
        assert block_keyword == "block", "must use block reference"
        return uri

    @classmethod
    def validate_genesis_hash(cls, uri):
        genesis_hash, _, _ = uri.replace("blockchain://", "").split("/")
        assert is_valid_hash(genesis_hash), f"hash is not valid: {genesis_hash}"
        return uri

    @classmethod
    def validate_block_hash(cls, uri):
        _, _, block_hash = uri.replace("blockchain://", "").split("/")
        assert is_valid_hash(block_hash), f"hash is not valid: {block_hash}"
        return uri
