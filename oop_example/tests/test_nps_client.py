from unittest.mock import mock_open

import pytest
import requests

import nps_client


def test_init_loads_api_key(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})

    client = nps_client.NPS(configuration={})

    assert client.api_key == "abc"
    assert client.limit == 3
    assert client.base_url.endswith("/api/v1")


def test_init_raises_when_api_key_missing(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {})

    with pytest.raises(ValueError):
        nps_client.NPS(configuration={})


def test_fetch_data_returns_endpoint_data(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})

    class Response:
        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return {"data": [{"id": "p1"}]}

    monkeypatch.setattr(nps_client.rq, "get", lambda *_, **__: Response())
    client = nps_client.NPS(configuration={})

    assert client.fetch_data("parks") == {"parks": [{"id": "p1"}]}


def test_fetch_data_handles_request_exception(monkeypatch):
    warnings = []
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})
    monkeypatch.setattr(nps_client.log, "warning", lambda msg: warnings.append(msg))
    monkeypatch.setattr(
        nps_client.rq,
        "get",
        lambda *_, **__: (_ for _ in ()).throw(requests.exceptions.RequestException("boom")),
    )
    client = nps_client.NPS(configuration={})

    assert client.fetch_data("parks") == {}
    assert warnings


def test_placeholder_methods_raise():
    with pytest.raises(Exception, match="Change me"):
        nps_client.NPS.path()
    with pytest.raises(Exception, match="Change me"):
        nps_client.NPS.primary_key()
    with pytest.raises(Exception, match="Change me"):
        nps_client.NPS.columns()
