from enum import Enum
from hashlib import md5


class Algorithm(str, Enum):
    MD5 = "md5"


def is_valid_hash(data: str) -> bool:
    if set(data.lower()) > set("1234567890abcdef"):
        return False

    if len(data) % 2 != 0:
        return False

    return True


def compute_checksum(content: bytes, algorithm: Algorithm = Algorithm.MD5) -> str:
    if algorithm is Algorithm.MD5:
        return md5(content).hexdigest()

    # TODO: Support sha3
    # TODO: Support sha256
    # TODO: Support IPFS CIDv0 & CIDv1
    # TODO: Support keccak256 (if even necessary, mentioned in EIP but not used)
    # TODO: Explore other algorithms needed
    else:
        raise ValueError("Unsupported algorithm")
