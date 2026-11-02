from pathlib import Path
import sys


def _connector_dir() -> Path:
    p = Path(__file__).resolve()
    while p.name != "weather_with_configuration":
        p = p.parent
    return p


sys.path.insert(0, str(_connector_dir()))
import connector as c  # noqa: E402


def test_intentional_failure_for_ci_red_path():
    # Intentionally wrong expectation to validate failing-test path in CI.
    assert any(t["table"] == "does_not_exist" for t in c.schema({}))
