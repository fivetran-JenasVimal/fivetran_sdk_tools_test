from unittest.mock import mock_open

import alerts_table
import articles_table
import nps_client
import park_table
import people_table


def _mock_config(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    monkeypatch.setattr(nps_client.json, "load", lambda _: {"api_key": "abc"})


def test_parks_process_data(monkeypatch):
    _mock_config(monkeypatch)
    monkeypatch.setattr(
        park_table.NPS,
        "fetch_data",
        lambda *_: {
            "parks": [
                {
                    "id": "p1",
                    "fullName": "Park A",
                    "description": "Desc",
                    "states": ["CA", "NV"],
                    "latitude": "1.5",
                    "longitude": "2.5",
                    "activities": [{"name": "Hiking"}],
                }
            ]
        },
    )
    rows = park_table.PARKS(configuration={}).process_data()
    assert rows[0]["park_id"] == "p1"
    assert rows[0]["state"] == "CA, NV"
    assert rows[0]["latitude"] == 1.5


def test_people_process_data(monkeypatch):
    _mock_config(monkeypatch)
    monkeypatch.setattr(
        people_table.NPS,
        "fetch_data",
        lambda *_: {
            "people": [
                {
                    "id": "x1",
                    "title": "Jane Doe",
                    "listingDescription": "Bio",
                    "url": "u",
                    "relatedParks": [{"parkCode": "abc"}],
                }
            ]
        },
    )
    rows = people_table.PEOPLE(configuration={}).process_data()
    assert rows[0]["person_id"] == "x1"
    assert rows[0]["related_parks"] == "abc"


def test_alerts_process_data(monkeypatch):
    _mock_config(monkeypatch)
    monkeypatch.setattr(
        alerts_table.NPS,
        "fetch_data",
        lambda *_: {
            "alerts": [
                {
                    "id": "a1",
                    "parkCode": "yell",
                    "title": "Alert",
                    "description": "Danger",
                    "category": "Closure",
                    "url": "u",
                }
            ]
        },
    )
    rows = alerts_table.ALERTS(configuration={}).process_data()
    assert rows[0]["alert_id"] == "a1"


def test_articles_process_data(monkeypatch):
    _mock_config(monkeypatch)
    monkeypatch.setattr(
        articles_table.NPS,
        "fetch_data",
        lambda *_: {
            "articles": [
                {
                    "id": "r1",
                    "title": "News",
                    "url": "u",
                    "listingDescription": "d",
                    "date": "2020-01-01",
                    "relatedParks": [{"parkCode": "abc", "fullName": "Park", "states": "CA"}],
                }
            ]
        },
    )
    rows = articles_table.ARTICLES(configuration={}).process_data()
    assert rows[0]["article_id"] == "r1"
    assert rows[0]["park_code"] == ["abc"]
