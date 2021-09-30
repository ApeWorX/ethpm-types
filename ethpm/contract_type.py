from typing import List, Optional, Set

from .abi import ABI
from .base import BaseModel


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
