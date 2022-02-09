import urllib.request
from typing import List, Optional

from pydantic import AnyUrl

from .base import BaseModel
from .utils import Algorithm, compute_checksum


class Compiler(BaseModel):
    name: str
    version: str
    settings: Optional[dict] = None
    contractTypes: Optional[List[str]] = None


class Checksum(BaseModel):
    """Checksum information about the contents of a source file."""

    algorithm: Algorithm
    hash: str


class Source(BaseModel):
    """Information about a source file included in a Package Manifest."""

    """Array of urls that resolve to the same source file."""
    urls: List[AnyUrl] = []

    """Hash of the source file."""
    checksum: Optional[Checksum] = None

    """Inlined contract source."""
    content: Optional[str] = None

    """Filesystem path of source file."""
    installPath: Optional[str] = None
    # NOTE: This was probably done for solidity, needs files cached to disk for compiling
    #       If processing a local project, code already exists, so no issue
    #       If processing remote project, cache them in ape project data folder

    """The type of the source file."""
    type: Optional[str] = None

    """The type of license associated with this source file."""
    license: Optional[str] = None
    # Set of `Source` objects that depend on this object
    # TODO: Add `SourceId` type and use instead of `str`
    references: Optional[List[str]] = None  # NOTE: Not a part of canonical EIP-2678 spec
    # NOTE: Set of source objects that this object depends on
    imports: Optional[List[str]] = None  # NOTE: Not a part of canonical EIP-2678 spec

    def load_content(self):
        """Loads resource at ``urls`` into ``content``."""
        if len(self.urls) == 0:
            return

        response = urllib.request.urlopen(self.urls[0])
        self.content = response.read().decode("utf-8")

    def compute_checksum(self, algorithm: Algorithm = Algorithm.MD5, force: bool = False):
        """
        Compute the checksum if ``content`` exists but ``checksum`` doesn't
        exist yet. Or compute the checksum regardless if ``force`` is ``True``.
        """
        if self.checksum and not force:
            return  # skip recalculating

        if not self.content:
            raise ValueError("Content not loaded yet. Can't compute checksum.")

        self.checksum = Checksum(  # type: ignore
            hash=compute_checksum(self.content.encode("utf8"), algorithm=algorithm),
            algorithm=algorithm,
        )
