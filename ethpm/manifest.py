from typing import Dict, List, Optional

from .base import BaseModel, root_validator
from .contract_type import ContractInstance, ContractType
from .source import Compiler, Source


class PackageMeta(BaseModel):
    authors: Optional[List[str]] = None
    license: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    links: Optional[Dict[str, str]] = None


class PackageManifest(BaseModel):
    # NOTE: Must not override this key
    manifest: str = "ethpm/3"
    # NOTE: ``name`` must begin lowercase, and be comprised of only ``[a-z0-9-]`` chars
    # NOTE: ``name`` should not exceed 255 chars in length
    name: Optional[str] = None
    # NOTE: ``version`` should be valid SemVer
    version: Optional[str] = None
    # NOTE: ``meta`` should be in all published packages
    meta: Optional[PackageMeta] = None
    # NOTE: ``sources`` source tree should be necessary and sufficient to compile
    #       all ``ContractType``s in manifest
    sources: Optional[Dict[str, Source]] = None
    # NOTE: ``contractTypes`` should only include types directly computed from manifest
    # NOTE: ``contractTypes`` should not include abstracts
    contractTypes: Optional[Dict[str, ContractType]] = None
    compilers: Optional[List[Compiler]] = None
    # NOTE: Keys must be a valid BIP122 URI chain definition
    # NOTE: Values must be a dict of ``ContractType.contractName`` => ``ContractInstance`` objects
    deployments: Optional[Dict[str, Dict[str, ContractInstance]]] = None
    # NOTE: keys must begin lowercase, and be comprised of only ``[a-z0-9-]`` chars
    #       (like ``PackageManifest.name``)
    # NOTE: keys should not exceed 255 chars in length (like ``PackageManifest.name``)
    # NOTE: values must be a Content Addressible URI that conforms to the same manifest
    #       version as ``manifest``
    buildDependencies: Optional[Dict[str, str]] = None

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
