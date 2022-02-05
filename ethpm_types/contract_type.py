from typing import Iterator, List, Optional

from hexbytes import HexBytes
from pydantic import Field

from .abi import ABI, ConstructorABI, EventABI, FallbackABI, MethodABI
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

    def to_bytes(self) -> Optional[HexBytes]:
        if self.bytecode:
            return HexBytes(self.bytecode)

        # TODO: Resolve links to produce dynamically linked bytecode
        return None


class ContractInstance(BaseModel):
    contract_type: str = Field(..., alias="contractType")
    address: str
    transaction: Optional[str] = None
    block: Optional[str] = None
    runtime_bytecode: Optional[Bytecode] = Field(None, alias="runtimeBytecode")


class SourceMapItem(BaseModel):
    # NOTE: `None` entry means this path was inserted by the compiler during codegen
    start: Optional[int]
    stop: Optional[int]
    contract_id: Optional[int]
    jump_code: str
    # NOTE: ignore "modifier_depth" keyword introduced in solidity >0.6.x


class SourceMap(BaseModel):
    __root__: str

    def parse(self) -> Iterator[SourceMapItem]:
        """
        Parses the source map string into a stream of ``SourceMapItem`` items.
        Useful for when parsing the map according to compiler-specific
        decompilation rules back to the source code language files.
        """

        item = None

        def extract_sourcemap_item(expanded_row, item_idx, previous_val=None):
            if len(expanded_row) > item_idx and expanded_row[item_idx] != "":
                return expanded_row[item_idx]

            else:
                return previous_val  # Use previous item (or None if no previous item)

        for i, row in enumerate(self.__root__.strip().split(";")):

            if row != "":
                expanded_row = row.split(":")

                if item is None:
                    start = int(extract_sourcemap_item(expanded_row, 0) or "-1")
                    stop = int(extract_sourcemap_item(expanded_row, 1) or "-1")
                    contract_id = int(extract_sourcemap_item(expanded_row, 2) or "-1")
                    jump_code = extract_sourcemap_item(expanded_row, 3) or ""

                else:
                    start = int(extract_sourcemap_item(expanded_row, 0, item.start or "-1"))
                    stop = int(extract_sourcemap_item(expanded_row, 1, item.stop or "-1"))
                    contract_id = int(
                        extract_sourcemap_item(expanded_row, 2, item.contract_id or "-1")
                    )
                    jump_code = extract_sourcemap_item(expanded_row, 3, item.jump_code or "")

                item = SourceMapItem.construct(
                    # NOTE: `-1` for these three entries means `None`
                    start=start if start != -1 else None,
                    stop=stop if stop != -1 else None,
                    contract_id=contract_id if contract_id != -1 else None,
                    jump_code=jump_code,
                )

            # else: use previous `item`
            # NOTE: Format of SourceMap is like `1:2:3:a;;4:5:6:b;;;`
            #       where an empty entry means to copy the previous step.

            if not item:
                # NOTE: This should only be true if there is no entry for the
                #       first step, which is illegal syntax for the sourcemap.
                raise Exception("Corrupted SourceMap")

            # NOTE: If row is empty, just yield previous step
            yield item


class ContractType(BaseModel):
    """
    A serializable type representing the type of a contract.
    For example, if you define your contract as ``contract MyContract`` (in Solidity),
    then ``MyContract`` would be the type.
    """

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

    def get_runtime_bytecode(self) -> Optional[HexBytes]:
        if self.runtime_bytecode:
            return self.runtime_bytecode.to_bytes()

        return None

    def get_deployment_bytecode(self) -> Optional[HexBytes]:
        if self.deployment_bytecode:
            return self.deployment_bytecode.to_bytes()

        return None

    @property
    def constructor(self) -> ConstructorABI:
        """
        The constructor of the contract, if it has one. For example,
        your smart-contract (in Solidity) may define a ``constructor() public {}``.
        This property contains information about the parameters needed to initialize
        a contract.
        """

        for abi in self.abi:
            if isinstance(abi, ConstructorABI):
                return abi

        return ConstructorABI(type="constructor")  # Use default constructor (no args)

    @property
    def fallback(self) -> FallbackABI:
        """
        The fallback method of the contract, if it has one. A fallback method
        is external, has no name, arguments, or return value, and gets invoked
        when the user attempts to call a method that does not exist.
        """

        for abi in self.abi:
            if isinstance(abi, FallbackABI):
                return abi

        return FallbackABI(type="fallback")  # Use default fallback (no args)

    @property
    def view_methods(self) -> List[MethodABI]:
        """
        The call-methods (read-only method, non-payable methods) defined in a smart contract.
        Returns:
            List[:class:`~ethpm_types.abi.ABI`]
        """

        return [abi for abi in self.abi if isinstance(abi, MethodABI) and not abi.is_stateful]

    @property
    def mutable_methods(self) -> List[MethodABI]:
        """
        The transaction-methods (stateful or payable methods) defined in a smart contract.
        Returns:
            List[:class:`~ethpm_types.abi.ABI`]
        """

        return [abi for abi in self.abi if isinstance(abi, MethodABI) and abi.is_stateful]

    @property
    def events(self) -> List[EventABI]:
        """
        The events defined in a smart contract.
        Returns:
            List[:class:`~ethpm_types.abi.ABI`]
        """

        return [abi for abi in self.abi if isinstance(abi, EventABI)]


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
