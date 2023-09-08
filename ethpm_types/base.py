import json
from typing import Any, Dict, no_type_check

from ethpm_types._pydantic_v1 import _BaseModel
from ethpm_types.utils import HexBytes


def ethpm_dumps(obj: Dict, **kwargs) -> str:
    json_dict = _dict_to_json_dict(obj)
    return json.dumps(json_dict, **kwargs)


def _dict_to_json_dict(obj: Dict) -> Dict:
    json_dict = {}
    key_fixed: Any
    val_fixed: Any
    for key, val in obj.items():
        key_fixed = _to_json_key(key)

        if isinstance(val, dict):
            val_fixed = _dict_to_json_dict(val)
        elif isinstance(val, list):
            val_fixed = [_to_json_key(x) for x in val]
        else:
            val_fixed = _to_json_key(val)

        json_dict[key_fixed] = val_fixed

    return json_dict


def _to_json_key(val: Any) -> Any:
    if isinstance(val, HexBytes):
        return val.hex()

    return val


class BaseModel(_BaseModel):
    class Config:
        json_dumps = ethpm_dumps

    def dict(self, *args, **kwargs) -> dict:
        # NOTE: We do this to accommodate the aliases needed for EIP-2678 compatibility
        if "by_alias" not in kwargs:
            kwargs["by_alias"] = True

        # EIP-2678: skip empty fields (at least by default)
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True

        return super().dict(*args, **kwargs)

    def json(self, *args, **kwargs) -> str:
        # NOTE: When serializing to IPFS, the canonical representation must be repeatable

        # EIP-2678: minified representation (at least by default)
        if "separators" not in kwargs:
            kwargs["separators"] = (",", ":")

        # EIP-2678: sort keys (at least by default)
        if "sort_keys" not in kwargs:
            kwargs["sort_keys"] = True

        # NOTE: We do this to accommodate the aliases needed for EIP-2678 compatibility
        if "by_alias" not in kwargs:
            kwargs["by_alias"] = True

        # EIP-2678: skip empty fields (at least by default)
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True

        return super().json(*args, **kwargs)

    @classmethod
    @no_type_check
    def _get_value(
        cls,
        v: Any,
        *args,
        **kwargs,
    ) -> Any:
        if isinstance(v, HexBytes):
            return v.hex()

        return super()._get_value(
            v,
            *args,
            **kwargs,
        )
