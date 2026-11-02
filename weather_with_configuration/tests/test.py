from pathlib import Path
import sys

import pytest


def _connector_dir() -> Path:
    p = Path(__file__).resolve()
    while p.name != "weather_with_configuration":
        p = p.parent
    return p


sys.path.insert(0, str(_connector_dir()))
import connector as c  # noqa: E402


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def _stub_logs(monkeypatch):
    for method in ("info", "debug", "warning", "error"):
        monkeypatch.setattr(c.log, method, lambda *args, **kwargs: None)


def test_validate_configuration_requires_zip_codes():
    with pytest.raises(ValueError):
        c.validate_configuration({})


def test_schema_contains_expected_tables():
    s = c.schema({})
    table_names = {t["table"] for t in s}
    assert table_names == {"forecast", "zip_code"}


def test_str2dt_parses_iso_timestamp():
    dt = c.str2dt("2026-01-01T00:00:00+0000")
    assert dt.year == 2026


def test_get_coordinates_from_zip(monkeypatch):
    payload = {
        "places": [{"latitude": "37.78", "longitude": "-122.42", "place name": "SF"}]
    }
    monkeypatch.setattr(c.rq, "get", lambda *_args, **_kwargs: _Resp(payload))

    (lat, lon), info = c.get_coordinates_from_zip("94108")
    assert (lat, lon) == (37.78, -122.42)
    assert info["zip_code"] == "94108"


def test_get_forecast_url(monkeypatch):
    payload = {"properties": {"forecast": "https://api.weather.gov/gridpoints/ABC/1,2/forecast"}}
    monkeypatch.setattr(c.rq, "get", lambda *_args, **_kwargs: _Resp(payload))

    url = c.get_forecast_url(37.78, -122.42)
    assert url.endswith("/forecast")


def test_update_upserts_and_checkpoints(monkeypatch):
    monkeypatch.setattr(c, "get_coordinates_from_zip", lambda _zip: ((37.78, -122.42), {"name": "SF"}))
    monkeypatch.setattr(c, "get_forecast_url", lambda _lat, _lon: "https://api.weather.gov/forecast")

    forecast_payload = {
        "properties": {
            "periods": [
                {
                    "name": "Tonight",
                    "startTime": "2026-01-01T01:00:00+0000",
                    "endTime": "2026-01-01T07:00:00+0000",
                }
            ]
        }
    }
    monkeypatch.setattr(c.rq, "get", lambda *_args, **_kwargs: _Resp(forecast_payload))

    events = []
    monkeypatch.setattr(c.op, "upsert", lambda table, data: events.append(("upsert", table, data)))
    monkeypatch.setattr(c.op, "checkpoint", lambda state: events.append(("checkpoint", state)))

    c.update({"zip_codes": "94108"}, {})

    upsert_tables = [e[1] for e in events if e[0] == "upsert"]
    assert "zip_code" in upsert_tables
    assert "forecast" in upsert_tables
    assert any(e[0] == "checkpoint" for e in events)
