"""Fault-injection tests for the open_meteo_marine_weather connector.

No network access: HTTP sessions are replaced with fakes and time.sleep is patched out.
"""

import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

import connector as c  # noqa: E402


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.exceptions.HTTPError(f"{self.status_code} error")
            err.response = self
            raise err

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._payload


class ScriptedSession:
    """Session whose get() plays back a list of responses or exceptions in order."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def get(self, url, params=None, timeout=None):
        self.calls += 1
        item = self._script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr(c.time, "sleep", lambda s: sleeps.append(s))
    # SDK logger needs an initialised log level; silence it in unit tests.
    monkeypatch.setattr(c.log, "info", lambda message: None)
    return sleeps


# --- fetch_data_with_retry: transient failures are retried ---


def test_retry_recovers_after_connection_errors(no_sleep):
    ok = FakeResponse(payload={"hourly": {}})
    session = ScriptedSession(
        [requests.exceptions.ConnectionError("reset"), requests.exceptions.ConnectionError("reset"), ok]
    )

    assert c.fetch_data_with_retry(session, "http://x") == {"hourly": {}}
    assert session.calls == 3
    assert no_sleep == [1, 2]  # exponential backoff


def test_retry_recovers_after_retryable_http_500(no_sleep):
    session = ScriptedSession([FakeResponse(500), FakeResponse(payload={"ok": True})])

    assert c.fetch_data_with_retry(session, "http://x") == {"ok": True}
    assert session.calls == 2
    assert no_sleep == [1]


def test_retry_recovers_after_429(no_sleep):
    session = ScriptedSession([FakeResponse(429), FakeResponse(payload={"ok": True})])

    assert c.fetch_data_with_retry(session, "http://x") == {"ok": True}
    assert session.calls == 2


# --- fetch_data_with_retry: exhausted or non-retryable failures raise ---


def test_connection_error_raises_after_max_retries():
    session = ScriptedSession([requests.exceptions.ConnectionError("down")] * c.__MAX_RETRIES)

    with pytest.raises(RuntimeError, match="Connection failed after 3 attempts"):
        c.fetch_data_with_retry(session, "http://x")
    assert session.calls == c.__MAX_RETRIES


def test_timeout_raises_after_max_retries():
    session = ScriptedSession([requests.exceptions.Timeout("slow")] * c.__MAX_RETRIES)

    with pytest.raises(RuntimeError, match="timed out after 3 attempts"):
        c.fetch_data_with_retry(session, "http://x")
    assert session.calls == c.__MAX_RETRIES


def test_persistent_500_raises_after_max_retries():
    session = ScriptedSession([FakeResponse(503)] * c.__MAX_RETRIES)

    with pytest.raises(RuntimeError, match="API request failed after 3 attempts"):
        c.fetch_data_with_retry(session, "http://x")
    assert session.calls == c.__MAX_RETRIES


def test_non_retryable_404_fails_fast(no_sleep):
    session = ScriptedSession([FakeResponse(404), FakeResponse(payload={})])

    with pytest.raises(RuntimeError, match="API request failed after 1 attempts"):
        c.fetch_data_with_retry(session, "http://x")
    assert session.calls == 1
    assert no_sleep == []


def test_malformed_json_is_not_retried_as_success(no_sleep):
    bad = FakeResponse(json_error=ValueError("not json"))
    session = ScriptedSession([bad])

    with pytest.raises(Exception):
        c.fetch_data_with_retry(session, "http://x")
    assert session.calls == 1


# --- validate_configuration: bad input is rejected before any API call ---


BASE_CONFIG = {"latitude": "37.7", "longitude": "-122.4"}


def test_valid_configuration_passes():
    c.validate_configuration(dict(BASE_CONFIG))


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"latitude": "<YOUR_LATITUDE>"}, "latitude"),
        ({"latitude": "abc"}, "latitude must be a valid number"),
        ({"latitude": "91"}, "latitude must be between -90 and 90"),
        ({"longitude": "-181"}, "longitude must be between -180 and 180"),
        ({"longitude": ""}, "longitude"),
    ],
)
def test_invalid_coordinates_are_rejected(overrides, message):
    config = {**BASE_CONFIG, **overrides}
    with pytest.raises(ValueError, match=message):
        c.validate_configuration(config)


def test_non_integer_forecast_days_is_rejected():
    with pytest.raises(ValueError, match="forecast_days must be a valid integer"):
        c.validate_configuration({**BASE_CONFIG, "forecast_days": "seven"})


def test_forecast_days_above_ceiling_is_rejected():
    too_many = str(c.__MAX_FORECAST_DAYS_CEILING + 1)
    with pytest.raises(ValueError):
        c.validate_configuration({**BASE_CONFIG, "forecast_days": too_many})


def test_past_days_above_ceiling_is_rejected():
    too_many = str(c.__MAX_PAST_DAYS_CEILING + 1)
    with pytest.raises(ValueError):
        c.validate_configuration({**BASE_CONFIG, "past_days": too_many})


# --- _safe_index: short or missing arrays return None instead of crashing ---


def test_safe_index_missing_key_returns_none():
    assert c._safe_index({}, "wave_height", 0) is None


def test_safe_index_short_array_returns_none():
    assert c._safe_index({"wave_height": [1.0]}, "wave_height", 5) is None


def test_safe_index_returns_value_in_range():
    assert c._safe_index({"wave_height": [1.0, 2.5]}, "wave_height", 1) == 2.5
