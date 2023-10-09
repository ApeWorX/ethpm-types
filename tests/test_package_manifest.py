import os
import tempfile
from pathlib import Path

import github
import pytest
import requests

from ethpm_types._pydantic_v1 import ValidationError
from ethpm_types.manifest import ALPHABET, NUMBERS, PackageManifest
from ethpm_types.source import Content, Source

ETHPM_SPEC_REPO = github.Github(os.environ.get("GITHUB_ACCESS_TOKEN", None)).get_repo(
    "ethpm/ethpm-spec"
)

EXAMPLES_RAW_URL = "https://raw.githubusercontent.com/ethpm/ethpm-spec/master/examples"


def test_can_generate_schema():
    PackageManifest.schema()


@pytest.mark.parametrize(
    "example_name",
    [f.name for f in ETHPM_SPEC_REPO.get_contents("examples")],  # type: ignore[union-attr]
)
def test_examples(example_name):
    example = requests.get(f"{EXAMPLES_RAW_URL}/{example_name}/v3.json")
    example_json = example.json()

    if "invalid" not in example_name:
        package = PackageManifest.parse_obj(example_json)
        assert package.dict() == example_json

        # NOTE: Also make sure that the encoding is exactly the same (per EIP-2678)
        actual = package.json()
        expected = example.text
        for idx, (c1, c2) in enumerate(zip(actual, expected)):
            # The following logic is because the strings being compared
            # are very long and this more accurately pinpoints
            # the failing section of the string, even on lower verbosity.
            buffer = 20
            start = max(0, idx - 10)
            actual_end = min(idx + buffer, len(actual))
            expected_end = min(idx + buffer, len(expected))
            actual_prefix = actual[start:actual_end]
            expected_prefix = expected[start:expected_end]
            fail_msg = (
                f"Differs at index: {idx}, "
                f"Actual: '{actual_prefix}', "
                f"Expected: '{expected_prefix}'"
            )
            assert c1 == c2, fail_msg

        if package.sources:
            for source_name, source in package.sources.items():
                # NOTE: Per EIP-2678, "Checksum is only required if content is missing"
                if not source.content:
                    assert source.content_is_valid(), f"Invalid checksum for '{source_name}'"

    else:
        with pytest.raises(ValidationError):
            PackageManifest.parse_obj(example_json).dict()


def test_open_zeppelin_contracts(oz_package):
    for source_name, source in oz_package.sources.items():
        # NOTE: Per EIP-2678, "Checksum is only required if content is missing"
        if not source.content:
            assert source.content_is_valid(), f"Invalid checksum for '{source_name}'"


def test_file_bases_dependency_url():
    manifest = PackageManifest(
        buildDependencies={"test-package": "file:///path/to/manifest/test-package.json"}
    )
    assert manifest.dependencies["test-package"] == "file:///path/to/manifest/test-package.json"


def test_getattr(package_manifest, solidity_contract):
    actual = package_manifest.SolidityContract
    expected = solidity_contract
    assert actual == expected


def test_get_contract_type(package_manifest, solidity_contract):
    actual = package_manifest.get_contract_type("SolidityContract")
    expected = solidity_contract
    assert actual == expected


def test_unpack_sources():
    foo_txt = Content(__root__={0: "line 0 in foo.txt"})
    baz_txt = Content(__root__={1: "line 1 in baz.txt"})
    sources = {"foo.txt": Source(content=foo_txt), "bar/nested/baz.txt": Source(content=baz_txt)}
    manifest = PackageManifest(sources=sources)

    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir) / "src"
        manifest.unpack_sources(destination)
        foo_expected = destination / "foo.txt"
        baz_expected = destination / "bar" / "nested" / "baz.txt"

        assert foo_expected.is_file()
        assert baz_expected.is_file()
        assert foo_expected.read_text() == str(foo_txt)
        assert baz_expected.read_text() == str(baz_txt)


def test_package_name_using_all_valid_characters():
    """
    Tests against a bug where we were unable to create a
    package manifest who's name contained all the valid
    characters.
    """
    name = "a" + "".join(list(ALPHABET.union(NUMBERS).union({"-"})))
    manifest = PackageManifest(name=name, version="0.1.0")
    assert manifest.name == name
