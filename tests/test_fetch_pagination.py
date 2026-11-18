import json
import json
import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from jalert.fetch import fetch_crossref, fetch_openalex


def response(payload):
    return 200, json.dumps(payload).encode("utf-8")


def openalex_work(suffix):
    return {
        "title": f"Paper {suffix}",
        "doi": f"https://doi.org/10.1000/{suffix}",
        "primary_location": {"landing_page_url": f"https://example.org/{suffix}"},
        "publication_date": "2026-06-01",
        "authorships": [],
        "abstract_inverted_index": {},
    }


def crossref_work(suffix):
    return {
        "title": [f"Paper {suffix}"],
        "DOI": f"10.1000/{suffix}",
        "URL": f"https://doi.org/10.1000/{suffix}",
        "published": {"date-parts": [[2026, 6, 1]]},
        "author": [],
    }


class FetchPaginationTests(unittest.TestCase):
    journal = {"name": "Test Journal", "issn": "1234-5678"}

    def test_openalex_uses_next_cursor_until_target_is_filled(self):
        pages = [
            {"meta": {"next_cursor": "cursor-2"}, "results": [openalex_work("a"), openalex_work("b")]},
            {"meta": {"next_cursor": None}, "results": [openalex_work("c")]},
        ]
        urls = []

        def fake_request(url, **_kwargs):
            urls.append(url)
            return response(pages[len(urls) - 1])

        with patch("jalert.fetch.http_request", side_effect=fake_request):
            items = fetch_openalex(self.journal, "2026-05-22", 3, None)

        self.assertEqual([item.title for item in items], ["Paper a", "Paper b", "Paper c"])
        self.assertEqual(len(urls), 2)
        self.assertEqual(parse_qs(urlparse(urls[0]).query)["cursor"], ["*"])
        self.assertEqual(parse_qs(urlparse(urls[1]).query)["cursor"], ["cursor-2"])

    def test_crossref_uses_next_cursor_until_target_is_filled(self):
        pages = [
            {"message": {"next-cursor": "cursor-2", "items": [crossref_work("a")]}},
            {"message": {"next-cursor": None, "items": [crossref_work("b")]}},
        ]
        urls = []

        def fake_request(url, **_kwargs):
            urls.append(url)
            return response(pages[len(urls) - 1])

        with patch("jalert.fetch.http_request", side_effect=fake_request):
            items = fetch_crossref(self.journal, "2026-05-22", 2, None)

        self.assertEqual([item.title for item in items], ["Paper a", "Paper b"])
        self.assertEqual(len(urls), 2)
        self.assertEqual(parse_qs(urlparse(urls[0]).query)["cursor"], ["*"])
        self.assertEqual(parse_qs(urlparse(urls[1]).query)["cursor"], ["cursor-2"])

    def test_repository_window_supports_six_month_backfill_and_safe_cap(self):
        from pathlib import Path

        config = json.loads(Path("config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["window"]["days"], 3)
        self.assertEqual(config["window"]["max_catchup_days"], 180)
        self.assertEqual(config["window"]["max_items_per_journal"], 5000)


if __name__ == "__main__":
    unittest.main()
