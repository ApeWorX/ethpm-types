from typing import Dict, List, Optional

from pydantic import AnyUrl, Field

from .base import BaseModel, root_validator
from .contract_type import ContractInstance, ContractType
from .source import Compiler, Source

ALPHABET = set("abcdefghijklmnopqrstuvwxyz".split())
NUMBERS = set("0123456789".split())


class PackageName(str):
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern="^[a-z][-a-z0-9]{0,254}$",
            examples=["my-token", "safe-math", "nft"],
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.check_length
        yield cls.check_first_character
        yield cls.check_valid_characters

    @classmethod
    def check_length(cls, value):
        assert 0 < len(value) < 256
        return value

    @classmethod
    def check_first_character(cls, value):
        assert value[0] in ALPHABET
        return value

    @classmethod
    def check_valid_characters(cls, value):
        assert set(value.split()) in (ALPHABET + NUMBERS + "-")
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"


class PackageMeta(BaseModel):
    authors: Optional[List[str]] = None
    license: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    links: Optional[Dict[str, AnyUrl]] = None


class PackageManifest(BaseModel):
    manifest: str = "ethpm/3"
    name: Optional[PackageName] = None
    # NOTE: ``version`` should be valid SemVer
    version: Optional[str] = None
    # NOTE: ``meta`` should be in all published packages
    meta: Optional[PackageMeta] = None
    # NOTE: ``sources`` source tree should be necessary and sufficient to compile
    #       all ``ContractType``s in manifest
    sources: Optional[Dict[str, Source]] = None
    # NOTE: ``contractTypes`` should only include types directly computed from manifest
    # NOTE: ``contractTypes`` should not include abstracts
    contract_types: Optional[Dict[str, ContractType]] = Field(None, alias="contractTypes")
    compilers: Optional[List[Compiler]] = None
    # NOTE: Keys must be a valid BIP122 URI chain definition
    # NOTE: Values must be a dict of ``ContractType.contractName`` => ``ContractInstance`` objects
    deployments: Optional[Dict[str, Dict[str, ContractInstance]]] = None
    # NOTE: keys must begin lowercase, and be comprised of only ``[a-z0-9-]`` chars
    #       (like ``PackageManifest.name``)
    # NOTE: keys should not exceed 255 chars in length (like ``PackageManifest.name``)
    # NOTE: values must be a Content Addressible URI that conforms to the same manifest
    #       version as ``manifest``
    dependencies: Optional[Dict[PackageName, AnyUrl]] = Field(None, alias="buildDependencies")

    @root_validator
    def check_valid_manifest_version(cls, values):
        assert "manifest" in values and values["manifest"] == "ethpm/3"
        return values

    @root_validator
    def check_both_version_and_name(cls, values):
        if "name" in values or "version" in values:
            assert "name" in values and "version" in values

        return values

    def __getattr__(self, attr_name: str):
        if self.contractTypes and attr_name in self.contractTypes:
            return self.contractTypes[attr_name]

        else:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{attr_name}'")
