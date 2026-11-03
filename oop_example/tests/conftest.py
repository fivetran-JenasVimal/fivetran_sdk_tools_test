import sys
import types


if "fivetran_connector_sdk" not in sys.modules:
    sdk = types.ModuleType("fivetran_connector_sdk")

    class Connector:
        def __init__(self, update, schema):
            self.update = update
            self.schema = schema

        def debug(self, configuration):
            return configuration

    class Logging:
        @staticmethod
        def warning(message):
            return message

    class Operations:
        @staticmethod
        def upsert(table, row):
            return table, row

    sdk.Connector = Connector
    sdk.Logging = Logging
    sdk.Operations = Operations
    sys.modules["fivetran_connector_sdk"] = sdk
