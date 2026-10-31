import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import connector  # noqa: E402


def test_add():
    assert connector.add(2, 3) == 5
