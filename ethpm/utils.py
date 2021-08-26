from hashlib import md5


def compute_checksum(source: bytes, algorithm: str = "md5") -> str:
    if algorithm == "md5":
        hasher = md5
    else:
        raise Exception("Unknown algorithm")

    return hasher(source).hexdigest()
