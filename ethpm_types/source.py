from typing import Iterator, List, Optional, Union

import requests
from cid import make_cid  # type: ignore

from .base import BaseModel
from .utils import CONTENT_ADDRESSED_SCHEMES, Algorithm, AnyUrl, Hex, compute_checksum


class Compiler(BaseModel):
    name: str
    """Which compiler was used in compilation."""

    version: str
    """
    The version of the compiler.
    The field should be OS agnostic (OS not included in the string) and take
    the form of either the stable version in semver format or if built on a nightly
    should be denoted in the form of <semver>-<commit-hash> ex: 0.4.8-commit.60cc1668.
    """

    settings: Optional[dict] = None
    """
    Any settings or configuration that was used in compilation. For the ``solc`` compiler,
    this should conform to the
    [Compiler Input and Output Description](https://docs.soliditylang.org/en/latest/using-the-compiler.html#compiler-input-and-output-json-description).
    """  # noqa: E501

    contractTypes: Optional[List[str]] = None
    """
    A list of the contract type names in this package
    that used this compiler to generate its outputs.
    """


class Checksum(BaseModel):
    """Checksum information about the contents of a source file."""

    algorithm: Algorithm
    """
    The algorithm used to generate the corresponding hash.
    Possible algorithms include, but are not limited to sha3, sha256, md5, keccak256.
    """

    hash: Hex
    """
    The hash of a source files contents generated with the corresponding algorithm.
    """


class Source(BaseModel):
    """Information about a source file included in a Package Manifest."""

    urls: List[AnyUrl] = []
    """Array of urls that resolve to the same source file."""

    checksum: Optional[Checksum] = None
    """
    Hash of the source file. Per EIP-2678,
    this field is only necessary if source must be fetched.
    """

    content: Optional[str] = None
    """Inlined contract source."""

    installPath: Optional[str] = None
    """
    Filesystem path of source file.
    **NOTE**: This was probably done for solidity, needs files cached to disk for compiling.
    If processing a local project, code already exists, so no issue.
    If processing remote project, cache them in ape project data folder
    """

    type: Optional[str] = None
    """The type of the source file."""

    license: Optional[str] = None
    """The type of license associated with this source file."""

    references: Optional[List[str]] = None
    """
    List of `Source` objects that depend on this object.
    **NOTE**: Not a part of canonical EIP-2678 spec.
    """
    # TODO: Add `SourceId` type and use instead of `str`

    imports: Optional[List[str]] = None
    """
    List of source objects that this object depends on.
    **NOTE**: Not a part of canonical EIP-2678 spec.
    """
    # TODO: Add `SourceId` type and use instead of `str`

    def __repr__(self) -> str:
        repr_id = "Source"

        if self.urls:
            # Favor URI when available.
            primary_uri = self.urls[0]
            repr_id = f"{repr_id} {primary_uri}"

        elif self.checksum:
            repr_id = f"{repr_id} {self.checksum.hash}"

        return f"<{repr_id}>"

    def __getitem__(self, number: Union[int, slice]):
        """
        Get a line or slice of lines from ``content``.

        Args:
            number (int, slice): The line index.
        """

        if self.content is None:
            raise IndexError("Source has no fetched content.")

        lines = self.content.splitlines()
        return lines[number]

    def __iter__(self) -> Iterator[str]:  # type: ignore
        if self.content is None:
            raise ValueError("Source has no fetched content.")

        return iter(self.content.splitlines())

    def __len__(self) -> int:
        if self.content is None:
            raise ValueError("Source has no fetched content.")

        return len(self.content.splitlines())

    def fetch_content(self) -> str:
        """
        Fetch the content for the given Source object.
        Loads resource at ``urls`` into ``content`` if not available.

        Returns:
            str
        """

        # NOTE: This is a trapdoor to bypass fetching logic if already available
        if self.content is not None:
            return self.content

        if len(self.urls) == 0:
            raise ValueError("No content to fetch.")

        for url in map(str, self.urls):
            # TODO: Have more robust handling of IPFS URIs
            if url.startswith("ipfs"):
                url = url.replace("ipfs://", "https://ipfs.io/ipfs/")

            response = requests.get(url)
            if response.status_code == 200:
                return response.text

        raise ValueError("Could not fetch content.")

    def calculate_checksum(self, algorithm: Algorithm = Algorithm.MD5) -> Checksum:
        """
        Compute the checksum of the ``Source`` object.
        Will short-circuit to content identifier if using content-addressed file references
        Fails if ``content`` isn't available locally or by fetching.

        Args:
            algorithm (Optional[:class:`~ethpm_types.utils.Algorithm`]): The algorithm to use
              to compute the checksum with. Defaults to MD5.

        Returns:
            :class:`~ethpm_types.source.Checksum`
        """

        # NOTE: Content-addressed URI schemes have checksum encoded directly in address.
        for url in self.urls:
            if url.scheme in CONTENT_ADDRESSED_SCHEMES:
                # TODO: Pull algorithm for checksum calc from codec
                cid = make_cid(url.host)
                return Checksum(hash=cid.multihash.hex(), algorithm=Algorithm.SHA256)

        content = self.fetch_content()
        return Checksum(
            hash=compute_checksum(content.encode("utf8"), algorithm=algorithm),
            algorithm=algorithm,
        )

    def content_is_valid(self) -> bool:
        """
        Return if content is corrupted.
        Will never be corrupted if content is locally available.
        If content is referenced by content addressed identifier,
        will not be corrupted either.
        If referenced from a server URL,
        then checksum must be present and will be validated against.

        Returns:
            bool
        """

        # NOTE: Per EIP-2678, checksum is not needed if content does not need to be fetched
        if self.content is not None:
            return True

        # NOTE: Per EIP-2678, Checksum is not required if a URL is content addressed.
        #       This is because the act of fetching the content validates the checksum.
        for url in self.urls:
            if url.scheme in CONTENT_ADDRESSED_SCHEMES:
                return True

        if self.checksum:
            return self.checksum == self.calculate_checksum(algorithm=self.checksum.algorithm)

        return False
