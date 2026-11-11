import pytest

import connector


def test_validate_configuration_requires_api_key():
    with pytest.raises(ValueError, match="api_key"):
        connector.validate_configuration({})


def test_schema_collects_selected_table_schemas(monkeypatch):
    class TableOne:
        def __init__(self, configuration):
            self.configuration = configuration

        @staticmethod
        def assign_schema():
            return {"table": "one"}

    class TableTwo:
        def __init__(self, configuration):
            self.configuration = configuration

        @staticmethod
        def assign_schema():
            return {"table": "two"}

    monkeypatch.setattr(connector, "selected_table", [TableOne, TableTwo])

    assert connector.schema({"api_key": "k"}) == [{"table": "one"}, {"table": "two"}]


def test_update_upserts_rows_for_each_table(monkeypatch):
    upserts = []

    class TableOne:
        def __init__(self, configuration):
            self.configuration = configuration

        @staticmethod
        def path():
            return "table_one"

        def process_data(self):
            return [{"id": 1}, {"id": 2}]

    class TableTwo:
        def __init__(self, configuration):
            self.configuration = configuration

        @staticmethod
        def path():
            return "table_two"

        def process_data(self):
            return [{"id": 10}]

    monkeypatch.setattr(connector, "selected_table", [TableOne, TableTwo])
    monkeypatch.setattr(connector.op, "upsert", lambda path, row: upserts.append((path, row)))

    connector.update({"api_key": "k"}, {})

    assert upserts == [
        ("table_one", {"id": 2}),
        ("table_one", {"id": 54}),
        ("table_two", {"id": 100}),
    ]
