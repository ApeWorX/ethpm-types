from typing import Iterator, List, Optional, Set

from pydantic import Field

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
    contract_type: str = Field(..., alias="contractType")
    address: str
    transaction: Optional[str] = None
    block: Optional[str] = None
    runtime_bytecode: Optional[Bytecode] = Field(None, alias="runtimeBytecode")


class SourceMapItem(BaseModel):
    start: int
    stop: int
    contract_id: int
    jump_code: str


class SourceMap(BaseModel):
    __root__: str

    def parse(self) -> Iterator[SourceMapItem]:
        """
        Parses the source map string into a stream of ``SourceMapItem`` items.
        Useful for when parsing the map according to compiler-specific
        decompilation rules back to the source code language files.
        """
        item = None
        for row in self.__root__.split(";"):

            if row:
                # NOTE: ignore "modifier depth" in solidity >0.6.x
                expanded_row = row.split(":")[:4]

                item = SourceMapItem.construct(
                    start=int(expanded_row[0]),
                    stop=int(expanded_row[1]),
                    contract_id=int(expanded_row[2]),
                    jump_code=expanded_row[3],
                )

            # else: use previous `item`
            # NOTE: Format of SourceMap is like `1:2:3:blah;;4:5:6:blah;;;`
            #       where an empty entry means to copy the previous step.

            if not item:
                # NOTE: This should only be true if there is no entry for the
                #       first step, which is illegal syntax for the sourcemap.
                raise Exception("Corrupted SourceMap")

            # NOTE: If row is empty, just yield previous step
            yield item


class ContractType(BaseModel):
    _keep_fields_: Set[str] = {"abi"}
    _skip_fields_: Set[str] = {"name"}
    # NOTE: Field is optional if `ContractAlias` is the same as `ContractName`
    name: Optional[str] = Field(None, alias="contractName")
    source_id: Optional[str] = Field(None, alias="sourceId")
    deployment_bytecode: Optional[Bytecode] = Field(None, alias="deploymentBytecode")
    runtime_bytecode: Optional[Bytecode] = Field(None, alias="runtimeBytecode")
    # abi, userdoc and devdoc must conform to spec
    abi: List[ABI] = []
    sourcemap: Optional[SourceMap] = None  # NOTE: Not a part of canonical EIP-2678 spec
    userdoc: Optional[dict] = None
    devdoc: Optional[dict] = None

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
    def txns(self) -> List[ABI]:
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
