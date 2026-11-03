import alerts_table
import articles_table
import park_table
import people_table


def test_alerts_table_schema_and_process(monkeypatch):
    assert alerts_table.ALERTS.path() == "alerts"
    assert alerts_table.ALERTS.primary_key() == ["alert_id"]
    assert alerts_table.ALERTS.assign_schema()["table"] == "alerts"

    monkeypatch.setattr(
        alerts_table.NPS,
        "fetch_data",
        lambda *_: {
            "alerts": [
                {
                    "id": "a1",
                    "parkCode": "acad",
                    "title": "Storm",
                    "description": "High winds",
                    "category": "Danger",
                    "url": "https://example.com/a1",
                }
            ]
        },
    )
    obj = alerts_table.ALERTS.__new__(alerts_table.ALERTS)
    out = obj.process_data()

    assert out == [
        {
            "alert_id": "a1",
            "park_code": "acad",
            "title": "Storm",
            "description": "High winds",
            "category": "Danger",
            "url": "https://example.com/a1",
        }
    ]


def test_people_table_schema_and_process(monkeypatch):
    assert people_table.PEOPLE.path() == "people"
    assert people_table.PEOPLE.primary_key() == ["person_id"]
    assert people_table.PEOPLE.assign_schema()["table"] == "people"

    monkeypatch.setattr(
        people_table.NPS,
        "fetch_data",
        lambda *_: {
            "people": [
                {
                    "id": "p1",
                    "title": "Jane Doe",
                    "listingDescription": "Ranger",
                    "url": "https://example.com/p1",
                    "relatedParks": [{"parkCode": "acad"}, {"parkCode": "yose"}],
                }
            ]
        },
    )
    obj = people_table.PEOPLE.__new__(people_table.PEOPLE)
    out = obj.process_data()

    assert out[0]["person_id"] == "p1"
    assert out[0]["name"] == "Jane Doe"
    assert out[0]["related_parks"] == "acad, yose"


def test_articles_table_schema_and_process(monkeypatch):
    assert articles_table.ARTICLES.path() == "articles"
    assert articles_table.ARTICLES.primary_key() == ["article_id"]
    assert articles_table.ARTICLES.assign_schema()["table"] == "articles"

    monkeypatch.setattr(
        articles_table.NPS,
        "fetch_data",
        lambda *_: {
            "articles": [
                {
                    "id": "ar1",
                    "title": "Trail Updates",
                    "url": "https://example.com/ar1",
                    "relatedParks": [{"parkCode": "acad", "fullName": "Acadia", "states": "ME"}],
                    "listingDescription": "Latest trail updates",
                    "date": "2026-01-01",
                }
            ]
        },
    )
    obj = articles_table.ARTICLES.__new__(articles_table.ARTICLES)
    out = obj.process_data()

    assert out[0]["article_id"] == "ar1"
    assert out[0]["park_code"] == ["acad"]
    assert out[0]["park_names"] == ["Acadia"]
    assert out[0]["states"] == ["ME"]


def test_parks_table_schema_and_process(monkeypatch):
    assert park_table.PARKS.path() == "parks"
    assert park_table.PARKS.primary_key() == ["park_id"]
    assert park_table.PARKS.assign_schema()["table"] == "parks"

    monkeypatch.setattr(
        park_table.NPS,
        "fetch_data",
        lambda *_: {
            "parks": [
                {
                    "id": "k1",
                    "fullName": "Acadia",
                    "description": "Beautiful park",
                    "states": ["ME"],
                    "latitude": "44.35",
                    "longitude": "-68.21",
                    "activities": [{"name": "Hiking"}, {"name": "Camping"}],
                }
            ]
        },
    )
    obj = park_table.PARKS.__new__(park_table.PARKS)
    out = obj.process_data()

    assert out[0]["park_id"] == "k1"
    assert out[0]["state"] == "ME"
    assert out[0]["latitude"] == 44.35
    assert out[0]["longitude"] == -68.21
    assert out[0]["activities"] == "Hiking, Camping"
