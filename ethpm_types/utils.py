import json
from enum import Enum
from hashlib import md5, sha3_256, sha256
from typing import Any, Dict, Optional, Sequence, Tuple

from eth_pydantic_types import HexStr

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


CONTENT_ADDRESSED_SCHEMES = {"ipfs"}


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
    data: Dict, include: Optional[Sequence[str]] = None, exclude: Optional[Sequence[str]] = None
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


SourceLocation = Tuple[int, int, int, int]

__all__ = [
    "Algorithm",
    "Annotated",
    "compute_checksum",
    "CONTENT_ADDRESSED_SCHEMES",
    "SourceLocation",
]
