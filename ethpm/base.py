from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    def dict(self, *args, **kwargs) -> dict:

        # EIP-2678: skip empty fields (at least by default)
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True

        return super().dict(*args, **kwargs)

    def json(self, *args, **kwargs) -> str:
        # NOTE: When serializing to IPFS, the canonical representation must be repeatable

        # EIP-2678: minified representation (at least by default)
        if "indent" not in kwargs:
            kwargs["indent"] = (",", ":")

        # EIP-2678: sort keys (at least by default)
        if "sort_keys" not in kwargs:
            kwargs["sort_keys"] = True

        return super().json(*args, **kwargs)
