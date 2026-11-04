import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jalert.cards import collect


class CardJournalFilterTests(unittest.TestCase):
    def test_card_wall_omits_journals_outside_current_allowlist(self):
        entries_by_report = {
            "2026-11-04.md": [
                {"title": "Current", "doi": "10.1/current", "journal": "Nature",
                 "topics": ["Climate"], "topic": "Climate", "score": 10,
                 "pubdate": "2026-11-04"},
                {"title": "Removed", "doi": "10.1/removed", "journal": "Old Journal",
                 "topics": ["Climate"], "topic": "Climate", "score": 9,
                 "pubdate": "2026-11-04"},
            ]
        }

        def fake_parse_report(path):
            return {"date": path.stem, "topics": [], "generated": ""}, entries_by_report[path.name]

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "2026-11-04.md"
            report.touch()
            with patch("jalert.cards.parse_report", side_effect=fake_parse_report):
                articles, reports, _topics = collect(Path(directory), ["Climate"], ["Nature"])

        self.assertEqual([article["journal"] for article in articles], ["Nature"])
        self.assertEqual(reports[0]["count"], 1)


if __name__ == "__main__":
    unittest.main()
