from nps_client import NPS


class ARTICLES(NPS):
    @staticmethod
    def path() -> str:
        return "articles"

    @staticmethod
    def primary_key():
        return ["article_id"]

    @staticmethod
    def assign_schema():
        return {
            "table": ARTICLES.path(),
            "primary_key": ARTICLES.primary_key(),
            "columns": {
                "article_id": "STRING",
                "title": "STRING",
                "url": "STRING",
                "park_code": "STRING",
                "park_names": "STRING",
                "states": "STRING",
                "listing_description": "STRING",
                "date": "STRING",
            },
        }

    def process_data(self):
        articles_response = NPS.fetch_data(self, ARTICLES.path())
        processed_articles = []

        for article in articles_response[ARTICLES.path()]:
            article_id = article.get("id", "Unknown ID")
            title = article.get("title", "No Title")
            url = article.get("url", "")
            park_code = [
                related_park.get("parkCode", "")
                for related_park in article.get("relatedParks", [])
            ]
            park_names = [
                related_park.get("fullName", "")
                for related_park in article.get("relatedParks", [])
            ]
            states = [
                related_park.get("states", "")
                for related_park in article.get("relatedParks", [])
            ]
            listing_description = article.get("listingDescription", "")
            date = article.get("date", "")

            processed_articles.append(
                {
                    "article_id": article_id,
                    "title": title,
                    "url": url,
                    "park_code": park_code,
                    "park_names": park_names,
                    "states": states,
                    "listing_description": listing_description,
                    "date": date,
                }
            )

        return processed_articles
