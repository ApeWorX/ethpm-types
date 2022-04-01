import urllib.request
from typing import List, Optional

from .base import BaseModel
from .utils import compute_checksum


class Compiler(BaseModel):
    name: str
    version: str
    settings: Optional[dict] = None
    contractTypes: Optional[List[str]] = None


class Checksum(BaseModel):
    algorithm: str
    hash: str


class Source(BaseModel):
    checksum: Optional[Checksum] = None
    urls: List[str] = []
    content: Optional[str] = None
    # TODO This was probably done for solidity, needs files cached to disk for compiling
    # If processing a local project, code already exists, so no issue
    # If processing remote project, cache them in ape project data folder
    installPath: Optional[str] = None
    type: Optional[str] = None
    license: Optional[str] = None
    # Set of `Source` objects that depend on this object
    # TODO: Add `SourceId` type and use instead of `str`
    references: Optional[List[str]] = None  # NOTE: Not a part of canonical EIP-2678 spec

    def load_content(self):
        """Loads resource at ``urls`` into ``content``."""
        if len(self.urls) == 0:
            return

        response = urllib.request.urlopen(self.urls[0])
        self.content = response.read().decode("utf-8")

    def compute_checksum(self, algorithm: str = "md5", force: bool = False):
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
