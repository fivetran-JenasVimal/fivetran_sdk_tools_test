import sys
from pathlib import Path

import pytest

# Make connector.py importable from tests/ by adding the connector folder
# (parent of this tests directory) to sys.path.
sys.path.insert(0, str(Path(__file__).parent.parent))

# Module under test.
import connector as c  # noqa: E402  (import must come after sys.path setup above)


class _Resp:
    # Minimal fake requests.Response used by monkeypatched HTTP calls.
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        # Simulate successful HTTP status.
        return None

    def json(self):
        # Return deterministic JSON payload provided by each test.
        return self._payload


@pytest.fixture(autouse=True)
def _stub_logs(monkeypatch):
    # Silence connector logs in test output; we only care about behavior/assertions.
    for method in ("info", "debug", "warning", "error"):
        monkeypatch.setattr(c.log, method, lambda *args, **kwargs: None)


def test_schema_has_expected_tables():
    # Connector schema should expose exactly these two destination tables.
    tables = {t["table"] for t in c.schema({})}
    assert tables == {"forecast", "zip_code"}


def test_validate_configuration_requires_zip_codes():
    # Missing required config key must raise.
    with pytest.raises(ValueError, match="zip_codes"):
        c.validate_configuration({})


def test_validate_configuration_passes_with_zip_codes():
    # Minimal valid config should pass validation.
    c.validate_configuration({"zip_codes": "94612"})

