from unittest.mock import mock_open

import pytest
import requests

import nps_client


def test_init_sets_api_key(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})

    client = nps_client.NPS(configuration={})

    assert client.api_key == "abc"
    assert client.limit == 3


def test_init_requires_api_key(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {})

    with pytest.raises(ValueError):
        nps_client.NPS(configuration={})


def test_fetch_data_success(monkeypatch):
    class Response:
        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return {"data": [{"id": "p1"}]}

    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})
    monkeypatch.setattr(nps_client.rq, "get", lambda *_, **__: Response())

    client = nps_client.NPS(configuration={})
    assert client.fetch_data("parks") == {"parks": [{"id": "p1"}]}


def test_fetch_data_handles_errors(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})
    monkeypatch.setattr(nps_client.log, "warning", lambda *_: None)
    monkeypatch.setattr(
        nps_client.rq,
        "get",
        lambda *_, **__: (_ for _ in ()).throw(requests.exceptions.RequestException("boom")),
    )

    client = nps_client.NPS(configuration={})
    assert client.fetch_data("parks") == {}


def test_placeholder_methods_raise():
    with pytest.raises(Exception, match="Change me"):
        nps_client.NPS.path()
    with pytest.raises(Exception, match="Change me"):
        nps_client.NPS.primary_key()
    with pytest.raises(Exception, match="Change me"):
        nps_client.NPS.columns()
