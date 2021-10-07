from hashlib import md5


def compute_checksum(source: bytes, algorithm: str = "md5") -> str:
    if algorithm == "md5":
        hasher = md5
    else:
        raise Exception("Unknown algorithm")

    return hasher(source).hexdigest()


def is_valid_hash(data: str) -> bool:
    if set(data.lower()) > set("1234567890abcdef"):
        return False

    if len(data) % 2 != 0:
        return False

    return True
