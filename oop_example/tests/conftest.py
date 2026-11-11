import sys
import types
from pathlib import Path


OOP_EXAMPLE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OOP_EXAMPLE_DIR))


sdk_module = types.ModuleType("fivetran_connector_sdk")


class _Connector:
    def __init__(self, update, schema):
        self.update = update
        self.schema = schema

    def debug(self, configuration):
        return self.update(configuration, {})


class _Logging:
    warnings = []

    @staticmethod
    def warning(message):
        _Logging.warnings.append(message)


class _Operations:
    upserts = []

    @staticmethod
    def upsert(path, row):
        _Operations.upserts.append((path, row))


sdk_module.Connector = _Connector
sdk_module.Logging = _Logging
sdk_module.Operations = _Operations

sys.modules.setdefault("fivetran_connector_sdk", sdk_module)
