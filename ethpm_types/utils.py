import json
from collections.abc import Sequence
from enum import Enum
from hashlib import md5, sha3_256, sha256
from typing import Annotated, Any, Optional, Union

from eth_pydantic_types import HexStr
from pydantic import AnyUrl as _AnyUrl
from pydantic import FileUrl

CONTENT_ADDRESSED_SCHEMES = {"ipfs"}
AnyUrl = Union[FileUrl, _AnyUrl]


class Algorithm(str, Enum):
    """
    Algorithm enum options MD5, SHA3, and SHA256.
    """

    MD5 = "md5"
    SHA3 = "sha3"
    SHA256 = "sha256"


def compute_checksum(content: bytes, algorithm: Algorithm = Algorithm.MD5) -> HexStr:
    """
    Calculate the checksum of the given content.

    Args:
        content (bytes): Content to hash.
        algorithm (:class:`~ethpm_types.utils.Algorithm`)" The algorithm to use.

    Returns:
        :class:`~ethpm_types.utils.Hex`
    """

    if isinstance(algorithm, str):
        algorithm = Algorithm(algorithm)

    if algorithm is Algorithm.MD5:
        return HexStr.from_bytes(md5(content).digest())

    elif algorithm is Algorithm.SHA3:
        return HexStr.from_bytes(sha3_256(content).digest())

    elif algorithm is Algorithm.SHA256:
        return HexStr.from_bytes(sha256(content).digest())

    # TODO: Support IPFS CIDv0 & CIDv1
    # TODO: Support keccak256 (if even necessary, mentioned in EIP but not used)
    # TODO: Explore other algorithms needed
    else:
        raise ValueError(f"Unsupported algorithm '{algorithm}'.")


def stringify_dict_for_hash(
    data: dict, include: Optional[Sequence[str]] = None, exclude: Optional[Sequence[str]] = None
) -> str:
    """
    Convert the given dict to a consistent str that can be used in hash.

    Args:
        data (Dict): The data to stringify.
        include (Optional[Sequence[str]]): Optionally filter keys to include.
        exclude (Optional[Sequence[str]]): Optionally filter keys to exclude.

    Returns:
        str
    """

    if include:
        data = {k: v for k, v in data.items() if k in include}
    if exclude:
        data = {k: v for k, v in data.items() if k not in exclude}

    # For hashing and ID.
    # Recursively sort dictionaries based on values
    def _sort(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: _sort(value[k]) for k in sorted(value)}
        elif isinstance(value, list):
            return [_sort(item) for item in value]

        return value

    sorted_settings = _sort(data or {})
    return json.dumps(sorted_settings, separators=(",", ":"), sort_keys=True)


def parse_signature(sig: str) -> tuple[str, list[tuple[str, str, str]], list[str]]:
    """
    Parse an event or function signature into name and inputs

    Args:
        sig (str): The string signature to parse.

    Returns:
        A tuple of (name, inputs, outputs) where inputs is a list of tuples of (type, indexed, arg
        name) and outputs is a list of types.
    """
    outsplit = sig.split(" -> ")
    std_sig = outsplit[0]
    outputs_maybe = ""
    if len(outsplit) > 1:
        outputs_maybe = outsplit[1]

    index = std_sig.find("(")
    name = std_sig[:index].strip()
    remainder = std_sig[index:].strip()[1:-1]
    inputs = _parse_signature_inputs(remainder)
    outputs = []

    if outputs_maybe:
        for outtyp in outputs_maybe.strip("()").split(","):
            outputs.append(outtyp.strip())

    return (name, inputs, outputs)


def _parse_signature_inputs(abi_str: str) -> list[tuple[str, str, str]]:
    if not abi_str:
        return []

    result = []
    type_ = ""
    indexed = ""
    name = ""
    characters = [c for c in abi_str]
    working_on = "type"
    while characters:
        character = characters.pop(0)
        if character == ",":
            # We reached the end of an input, or some random space.
            result.append((type_, indexed, name))
            type_ = indexed = name = ""
            working_on = "type"

            # Clear random spaces.
            while characters[0] == " ":
                characters.pop(0)

            continue

        if character == " ":
            if working_on == "type":
                working_on = "name"

            if "".join(characters).startswith("indexed "):
                indexed = "indexed"
                characters = characters[8:]

            continue

        elif character == "(":
            # Is a tuple. Find the end of the tuple.
            type_ = "("
            end_tuple = None
            while end_tuple != ")":
                end_tuple = characters.pop(0)
                type_ = f"{type_}{end_tuple}"

        elif working_on == "type":
            type_ = f"{type_}{character}"

        elif working_on == "name":
            name = f"{name}{character}"

    # Add the last input.
    if type_:
        result.append((type_, indexed, name))

    return result


SourceLocation = tuple[int, int, int, int]

__all__ = [
    "Algorithm",
    "Annotated",
    "compute_checksum",
    "CONTENT_ADDRESSED_SCHEMES",
    "SourceLocation",
]
