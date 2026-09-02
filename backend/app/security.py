import hashlib


def md5_hash(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()
