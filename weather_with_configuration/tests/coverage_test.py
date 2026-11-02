from pathlib import Path
import sys


def _connector_dir() -> Path:
    p = Path(__file__).resolve()
    while p.name != "weather_with_configuration":
        p = p.parent
    return p


sys.path.insert(0, str(_connector_dir()))
import connector as c  # noqa: E402


def test_schema_has_forecast_table():
    assert any(t["table"] == "forecast" for t in c.schema({}))
