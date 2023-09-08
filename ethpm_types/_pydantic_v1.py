# TODO: Can delete this file once we full migrate to v2.
try:
    from pydantic.v1 import AnyUrl as _AnyUrl  # type: ignore
    from pydantic.v1 import BaseModel as _BaseModel  # type: ignore
    from pydantic.v1 import (  # type: ignore
        Extra,
        Field,
        FileUrl,
        ValidationError,
        root_validator,
        validator,
    )
except ImportError:
    from pydantic import AnyUrl as _AnyUrl  # type: ignore
    from pydantic import BaseModel as _BaseModel  # type: ignore
    from pydantic import (  # type: ignore
        Extra,
        Field,
        FileUrl,
        ValidationError,
        root_validator,
        validator,
    )
