import alerts_table
import articles_table
import park_table
import people_table


def test_table_schemas_are_wired_to_path_and_primary_keys():
    for table in [alerts_table.ALERTS, articles_table.ARTICLES, park_table.PARKS, people_table.PEOPLE]:
        schema = table.assign_schema()
        assert schema["table"] == table.path()
        assert schema["primary_key"] == table.primary_key()
        assert isinstance(schema["columns"], dict)
        assert schema["columns"]


def test_alerts_process_data_maps_fields(monkeypatch):
    monkeypatch.setattr(
        alerts_table.NPS,
        "fetch_data",
        lambda *_: {
            "alerts": [
                {
                    "id": "100",
                    "parkCode": "yose",
                    "title": "Alert title",
                    "description": "Alert description",
                    "category": "Park Closure",
                    "url": "https://example.com/alert",
                }
            ]
        },
    )

    alerts = alerts_table.ALERTS.__new__(alerts_table.ALERTS)
    assert alerts.process_data() == [
        {
            "alert_id": "a1",
            "park_code": "yose",
            "title": "Alert title",
            "description": "Alert description",
            "category": "Park Closure",
            "url": "https://example.com/alert",
        }
    ]


def test_articles_process_data_maps_related_parks(monkeypatch):
    monkeypatch.setattr(
        articles_table.NPS,
        "fetch_data",
        lambda *_: {
            "articles": [
                {
                    "id": "ar1",
                    "title": "Article title",
                    "url": "https://example.com/article",
                    "relatedParks": [
                        {"parkCode": "yose", "fullName": "Yosemite", "states": "CA"},
                        {"parkCode": "grca", "fullName": "Grand Canyon", "states": "AZ"},
                    ],
                    "listingDescription": "Article description",
                    "date": "2026-01-01",
                }
            ]
        },
    )

    articles = articles_table.ARTICLES.__new__(articles_table.ARTICLES)
    assert articles.process_data() == [
        {
            "article_id": "ar1",
            "title": "Article title",
            "url": "https://example.com/article",
            "park_code": ["yose", "grca"],
            "park_names": ["Yosemite", "Grand Canyon"],
            "states": ["CA", "AZ"],
            "listing_description": "Article description",
            "date": "2026-01-01",
        }
    ]


def test_parks_process_data_casts_coordinates(monkeypatch):
    monkeypatch.setattr(
        park_table.NPS,
        "fetch_data",
        lambda *_: {
            "parks": [
                {
                    "id": "p1",
                    "fullName": "Yosemite National Park",
                    "description": "Beautiful valley",
                    "states": ["CA"],
                    "latitude": "37.8651",
                    "longitude": "-119.5383",
                    "activities": [{"name": "Hiking"}, {"name": "Camping"}],
                }
            ]
        },
    )

    parks = park_table.PARKS.__new__(park_table.PARKS)
    assert parks.process_data() == [
        {
            "park_id": "p1",
            "name": "Yosemite National Park",
            "description": "Beautiful valley",
            "state": "CA",
            "latitude": 37.8651,
            "longitude": -119.5383,
            "activities": "Hiking, Camping",
        }
    ]


def test_people_process_data_maps_related_parks(monkeypatch):
    monkeypatch.setattr(
        people_table.NPS,
        "fetch_data",
        lambda *_: {
            "people": [
                {
                    "id": "person1",
                    "title": "John Muir",
                    "listingDescription": "Naturalist",
                    "url": "https://example.com/person",
                    "relatedParks": [{"parkCode": "yose"}, {"parkCode": "seki"}],
                }
            ]
        },
    )

    people = people_table.PEOPLE.__new__(people_table.PEOPLE)
    assert people.process_data() == [
        {
            "person_id": "person1",
            "name": "John Muir",
            "title": "Naturalist",
            "description": "Naturalist",
            "url": "https://example.com/person",
            "related_parks": "yose, seki",
        }
    ]
