import sys
from pathlib import Path

import pytest

# Put the connector's own folder (one level up from tests/) on the import
# path, so `import connector` below finds connector.py even though this
# test file lives in a subfolder.
sys.path.insert(0, str(Path(__file__).parent.parent))

import connector as c  # noqa: E402  (import must come after sys.path setup above)


def test_schema_has_expected_tables():
    # schema({}) returns the list of table definitions the connector exposes.
    # Pass an empty config since schema() here doesn't use it.
    tables = {t["table"] for t in c.schema({})}
    # Fails if a table gets renamed, removed, or an extra one is added.
    assert tables == {"forecast", "zip_code"}


def test_validate_configuration_requires_zip_codes():
    # An empty config is missing "zip_codes", so this must raise ValueError
    # with a message mentioning "zip_codes" - catches both a dropped check
    # and a check whose error message silently changed.
    with pytest.raises(ValueError, match="zip_codes"):
        c.validate_configuration({})


def test_validate_configuration_passes_with_zip_codes():
    # A valid config must NOT raise. No assert needed: the test only fails
    # if this line throws an exception.
    c.validate_configuration({"zip_codes": "94612"})
