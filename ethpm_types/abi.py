from typing import List, Optional, Union

from .base import BaseModel


class ABIType(BaseModel):
    name: Optional[str] = None  # NOTE: Tuples don't have names by default
    indexed: Optional[bool] = None  # Only event ABI types should have this field
    type: Union[str, "ABIType"]
    internalType: Optional[str] = None

    @property
    def canonical_type(self) -> str:
        if isinstance(self.type, str):
            return self.type

        else:
            # Recursively discover the canonical type
            return self.type.canonical_type


def encode_arg(arg: ABIType) -> str:
    encoded_arg = arg.canonical_type
    # For events (handles both None and False conditions)
    if arg.indexed:
        encoded_arg += " indexed"
    if arg.name:
        encoded_arg += f" {arg.name}"
    return encoded_arg


class ABI(BaseModel):
    name: Optional[str] = None
    inputs: Optional[List[ABIType]] = None
    outputs: Optional[List[ABIType]] = None
    # ABI v2 Field
    # NOTE: Only functions have this field
    stateMutability: Optional[str] = None
    # NOTE: Only events have this field
    anonymous: Optional[bool] = None
    # TODO: Handle events and functions separately (maybe also default and constructor)
    #       Would parse based on value of type here, so some indirection required
    #       Might make most sense to add to ``ContractType`` as a serde extension
    type: str

    @property
    def signature(self) -> str:
        """
        String representing the function/event signature, which includes the arg names and types,
        and output names (if any) and type(s)
        """
        name = self.name if (self.type == "function" or self.type == "event") else self.type

        input_args = ", ".join(map(encode_arg, self.inputs or []))
        output_args = ""

        if self.outputs:
            output_args = " -> "
            if len(self.outputs) > 1:
                output_args += "(" + ", ".join(map(encode_arg, self.outputs)) + ")"
            else:
                output_args += encode_arg(self.outputs[0])

        return f"{name}({input_args}){output_args}"

    @property
    def selector(self) -> str:
        """
        String representing the function selector, used to compute ``method_id`` and ``event_id``.
        """
        name = self.name if (self.type == "function" or self.type == "event") else self.type
        # NOTE: There is no space between input args for selector
        input_names = ",".join(i.canonical_type for i in (self.inputs or []))
        return f"{name}({input_names})"

    @property
    def is_event(self) -> bool:
        return self.anonymous is not None

    @property
    def is_payable(self) -> bool:
        return self.stateMutability == "payable"

    @property
    def is_stateful(self) -> bool:
        return self.stateMutability not in ("view", "pure")
