from typing import Callable, Iterator, List, Optional, Union

from eth_utils import add_0x_prefix
from hexbytes import HexBytes
from pydantic import Field, validator

from .abi import ABI, ConstructorABI, EventABI, FallbackABI, MethodABI
from .base import BaseModel
from .utils import Hex, is_valid_hex


# TODO link references & link values are for solidity, not used with Vyper
# Offsets are for dynamic links, e.g. EIP1167 proxy forwarder
class LinkDependency(BaseModel):
    offsets: List[int]
    """
    The locations within the corresponding bytecode where the value for this
    link value was written. These locations are 0-indexed from the beginning
    of the bytes representation of the corresponding bytecode.
    """

    type: str
    """
    The value type for determining what is encoded when linking the corresponding
    bytecode.
    """

    value: str
    """
    The value which should be written when linking the corresponding bytecode.
    """


class LinkReference(BaseModel):
    offsets: List[int]
    """
    An array of integers, corresponding to each of the start positions
    where the link reference appears in the bytecode. Locations are 0-indexed
    from the beginning of the bytes representation of the corresponding bytecode.
    This field is invalid if it references a position that is beyond the end of
    the bytecode.
    """

    length: int
    """
    The length in bytes of the link reference.
    This field is invalid if the end of the defined link reference exceeds the
    end of the bytecode.
    """

    name: Optional[str] = None
    """
    A valid identifier for the reference.
    Any link references which should be linked with the same link value should
    be given the same name.
    """


class Bytecode(BaseModel):
    bytecode: Optional[Hex] = None
    """
    A string containing the 0x prefixed hexadecimal representation of the bytecode.
    """

    linkReferences: Optional[List[LinkReference]] = None
    """
    The locations in the corresponding bytecode which require linking.
    """

    linkDependencies: Optional[List[LinkDependency]] = None
    """
    The link values that have been used to link the corresponding bytecode.
    """

    @validator("bytecode", pre=True)
    def prefix_bytecode(cls, v):
        if not v:
            return None
        return add_0x_prefix(v)

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
    """
    Any of the contract type names included in this Package
    or any of the contract type names found in any of the package dependencies
    from the ``buildDependencies`` section of the Package Manifest.
    """

    address: Hex
    """The contract address."""

    transaction: Optional[Hex] = None
    """The transaction hash from which the contract was created."""

    block: Optional[Hex] = None
    """
    The block hash in which this the transaction which created this
    contract instance was mined.
    """

    runtime_bytecode: Optional[Bytecode] = Field(None, alias="runtimeBytecode")
    """
    The runtime portion of bytecode for this Contract Instance.
    When present, the value from this field supersedes the ``runtimeBytecode``
    from the :class:`~ethpm_types.contract_type.ContractType` for this
    ``ContractInstance``.
    """


class SourceMapItem(BaseModel):
    # NOTE: `None` entry means this path was inserted by the compiler during codegen
    start: Optional[int]
    stop: Optional[int]
    contract_id: Optional[int]
    jump_code: str
    # NOTE: ignore "modifier_depth" keyword introduced in solidity >0.6.x


class SourceMap(BaseModel):
    """
    As part of the AST output, the compiler provides the range of the source code
    that is represented by the respective node in the AST.
    This can be used for various purposes ranging from static analysis tools that
    report errors based on the AST and debugging tools that highlight local variables
    and their uses.

    `Solidity Doc <https://docs.soliditylang.org/en/v0.8.15/internals/source_mappings.html>`__.
    """

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


class ABIList(list):
    """
    Adds selection by name, selector and keccak(selector).
    """

    def __init__(
        self,
        iterable=(),
        *,
        selector_id_size=32,
        selector_hash_fn: Optional[Callable[[str], bytes]] = None,
    ):
        self._selector_id_size = selector_id_size
        self._selector_hash_fn = selector_hash_fn
        super().__init__(iterable)

    def __getitem__(  # type: ignore
        self, item: Union[int, slice, str, HexBytes, bytes, MethodABI, EventABI]
    ):
        try:
            # selector
            if isinstance(item, str) and "(" in item:
                return next(abi for abi in self if abi.selector == item)
            # name, could be ambiguous
            elif isinstance(item, str):
                return next(abi for abi in self if abi.name == item)
            # hashed selector, like log.topics[0] or tx.data
            # NOTE: Will fail with `ImportError` if `item` is `bytes` and `eth-hash` has no backend
            elif isinstance(item, (bytes, HexBytes)) and self._selector_hash_fn:
                return next(
                    abi
                    for abi in self
                    if self._selector_hash_fn(abi.selector)[: self._selector_id_size]
                    == item[: self._selector_id_size]
                )
            elif isinstance(item, (MethodABI, EventABI)):
                return next(abi for abi in self if abi.selector == item.selector)
        except StopIteration:
            raise KeyError(item)

        # handle int, slice
        return super().__getitem__(item)  # type: ignore

    def __contains__(self, item: Union[str, bytes]) -> bool:  # type: ignore
        if isinstance(item, (int, slice)):
            return False
        try:
            self[item]
            return True
        except (KeyError, IndexError):
            return False


class ContractType(BaseModel):
    """
    A serializable type representing the type of a contract.
    For example, if you define your contract as ``contract MyContract`` (in Solidity),
    then ``MyContract`` would be the type.
    """

    name: Optional[str] = Field(None, alias="contractName")
    """
    The name of the contract type. The field is optional if ``ContractAlias``
    is the same as ``ContractName``.
    """

    source_id: Optional[str] = Field(None, alias="sourceId")
    """
    The global source identifier for the source file from which this contract type was generated.
    """

    deployment_bytecode: Optional[Bytecode] = Field(None, alias="deploymentBytecode")
    """The bytecode for the ContractType."""

    runtime_bytecode: Optional[Bytecode] = Field(None, alias="runtimeBytecode")
    """The unlinked 0x-prefixed runtime portion of bytecode for this ContractType."""

    abi: List[ABI] = []
    """The application binary interface to the contract."""

    sourcemap: Optional[SourceMap] = None
    """
    The range of the source code that is represented by the respective node in the AST.
    **NOTE**: This is not part of the canonical EIP-2678 spec.
    """

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

        constructor_abi: Optional[ConstructorABI] = None
        for abi in self.abi:
            if isinstance(abi, ConstructorABI):
                constructor_abi = abi
                break

        constructor_abi = constructor_abi or ConstructorABI(
            type="constructor"
        )  # Use default constructor (no args)
        constructor_abi.contract_type = self
        return constructor_abi

    @property
    def fallback(self) -> FallbackABI:
        """
        The fallback method of the contract, if it has one. A fallback method
        is external, has no name, arguments, or return value, and gets invoked
        when the user attempts to call a method that does not exist.
        """

        fallback_abi: Optional[FallbackABI] = None
        for abi in self.abi:
            if isinstance(abi, FallbackABI):
                fallback_abi = abi
                break

        fallback_abi = fallback_abi or FallbackABI(
            type="fallback"
        )  # Use default fallback (no args)
        fallback_abi.contract_type = self
        return fallback_abi

    @property
    def view_methods(self) -> List[MethodABI]:
        """
        The call-methods (read-only method, non-payable methods) defined in a smart contract.
        Returns:
            List[:class:`~ethpm_types.abi.ABI`]
        """

        method_abis = [
            abi for abi in self.abi if isinstance(abi, MethodABI) and not abi.is_stateful
        ]
        for abi in method_abis:
            abi.contract_type = self

        return ABIList(
            method_abis,
            selector_id_size=4,
            selector_hash_fn=self._selector_hash_fn,
        )

    @property
    def mutable_methods(self) -> List[MethodABI]:
        """
        The transaction-methods (stateful or payable methods) defined in a smart contract.
        Returns:
            List[:class:`~ethpm_types.abi.ABI`]
        """

        method_abis = [abi for abi in self.abi if isinstance(abi, MethodABI) and abi.is_stateful]
        for abi in method_abis:
            abi.contract_type = self

        return ABIList(
            method_abis,
            selector_id_size=4,
            selector_hash_fn=self._selector_hash_fn,
        )

    @property
    def events(self) -> List[EventABI]:
        """
        The events defined in a smart contract.
        Returns:
            List[:class:`~ethpm_types.abi.ABI`]
        """

        event_abis = [abi for abi in self.abi if isinstance(abi, EventABI)]
        for abi in event_abis:
            abi.contract_type = self

        return ABIList(
            event_abis,
            selector_hash_fn=self._selector_hash_fn,
        )

    def _selector_hash_fn(self, selector: str) -> bytes:
        # keccak is the default on most ecosystems, other ecosystems can subclass to override it
        from eth_utils import keccak

        return keccak(text=selector)


class BIP122_URI(str):
    """
    A URI scheme for looking up blocks.
    `BIP-122 <https://github.com/bitcoin/bips/blob/master/bip-0122.mediawiki>`__.

    URI Format::

        blockchain://<chain>/<block>/<hash>

    """

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
        yield cls.validate_block_hash

    @classmethod
    def validate_uri(cls, uri):
        if not uri.startswith("blockchain://"):
            raise ValueError("Must use 'blockchain' protocol.")

        if len(uri.replace("blockchain://", "").split("/")) != 3:
            raise ValueError("Must be referenced via <genesis_hash>/block/<block_hash>.")

        _, block_keyword, _ = uri.replace("blockchain://", "").split("/")
        if block_keyword != "block":
            raise ValueError("Must use block reference.")

        return uri

    @classmethod
    def validate_genesis_hash(cls, uri):
        genesis_hash, _, _ = uri.replace("blockchain://", "").split("/")
        if not is_valid_hex("0x" + genesis_hash):
            raise ValueError(f"Hash is not valid: {genesis_hash}.")

        if len(genesis_hash) != 64:
            raise ValueError(f"Hash is not valid length: {genesis_hash}.")

        return uri

    @classmethod
    def validate_block_hash(cls, uri):
        _, _, block_hash = uri.replace("blockchain://", "").split("/")
        if not is_valid_hex("0x" + block_hash):
            raise ValueError(f"Hash is not valid: {block_hash}.")

        if len(block_hash) != 64:
            raise ValueError(f"Hash is not valid length: {block_hash}.")

        return uri
