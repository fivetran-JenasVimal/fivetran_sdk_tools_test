import pytest

import connector


def test_validate_configuration_requires_api_key():
    with pytest.raises(ValueError):
        connector.validate_configuration({})


def test_schema_returns_table_schemas(monkeypatch):
    class DummyTable:
        @staticmethod
        def path():
            return "dummy"

        def __init__(self, configuration):
            self.configuration = configuration

        @staticmethod
        def assign_schema():
            return {"table": "dummy", "primary_key": ["id"], "columns": {"id": "STRING"}}

    monkeypatch.setattr(connector, "selected_table", [DummyTable])
    out = connector.schema({"api_key": "k"})

    assert out == [{"table": "dummy", "primary_key": ["id"], "columns": {"id": "STRING"}}]


def test_update_upserts_rows(monkeypatch):
    calls = []

    class DummyTable:
        @staticmethod
        def path():
            return "dummy"

        def __init__(self, configuration):
            self.configuration = configuration

        def process_data(self):
            return [{"id": "1"}, {"id": "2"}]

    monkeypatch.setattr(connector, "selected_table", [DummyTable])
    monkeypatch.setattr(connector.op, "upsert", lambda table, row: calls.append((table, row)))

    connector.update({"api_key": "k"}, state={})

    assert calls == [("dummy", {"id": "1"}), ("dummy", {"id": "2"})]
