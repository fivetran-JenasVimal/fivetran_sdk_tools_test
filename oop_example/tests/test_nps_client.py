from unittest.mock import mock_open

import pytest

import nps_client


def test_init_sets_defaults_from_configuration_file(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data='{"api_key":"ignored"}'))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "secret"})

    client = nps_client.NPS(configuration={})

    assert client.api_key == "secret"
    assert client.limit == 3
    assert client.base_url == "https://developer.nps.gov/api/v1"


def test_init_raises_when_api_key_missing(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {})

    with pytest.raises(ValueError, match="API key is missing"):
        nps_client.NPS(configuration={})


def test_fetch_data_returns_endpoint_data(monkeypatch):
    class Response:
        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return {"data": [{"id": "p1"}]}

    monkeypatch.setattr(nps_client.rq, "get", lambda *_args, **_kwargs: Response())

    client = nps_client.NPS.__new__(nps_client.NPS)
    client.api_key = "k"
    client.limit = 3
    client.base_url = "https://example.com"

    assert client.fetch_data("parks") == {"parks": [{"id": "p1"}]}


def test_fetch_data_returns_empty_on_request_error(monkeypatch):
    warnings = []

    def _raise(*_args, **_kwargs):
        raise nps_client.rq.exceptions.RequestException("boom")

    monkeypatch.setattr(nps_client.rq, "get", _raise)
    monkeypatch.setattr(nps_client.log, "warning", lambda message: warnings.append(message))

    client = nps_client.NPS.__new__(nps_client.NPS)
    client.api_key = "k"
    client.limit = 3
    client.base_url = "https://example.com"

    assert client.fetch_data("parks") == {}
    assert len(warnings) == 1
