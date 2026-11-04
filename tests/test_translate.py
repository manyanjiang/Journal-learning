import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jalert.translate import translate_articles


class TranslationCacheTests(unittest.TestCase):
    def test_translates_and_reuses_cached_fields(self):
        article = {
            "doi": "10.1234/example",
            "title": "A study of clean energy",
            "abstract": "We assess clean energy pathways.",
        }

        def response_for(request, timeout):
            from urllib.parse import parse_qs

            texts = parse_qs(request.data.decode("utf-8"))["text"]
            payload = json.dumps({"translations": [{"text": "中文：" + text} for text in texts]})
            return io.BytesIO(payload.encode("utf-8"))

        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "translations.json"
            with patch("jalert.translate.urllib.request.urlopen", side_effect=response_for) as call:
                translated = translate_articles([article], cache_path, api_key="test-key")
                self.assertEqual(call.call_count, 1)
                self.assertEqual(translated[article["doi"]]["title"], "中文：A study of clean energy")
                self.assertEqual(translated[article["doi"]]["abstract"],
                                 "中文：We assess clean energy pathways.")

                reused = translate_articles([article], cache_path, api_key="test-key")
                self.assertEqual(call.call_count, 1)
                self.assertEqual(reused, translated)

    def test_changed_source_does_not_show_stale_translation_without_key(self):
        article = {"doi": "10.1234/example", "title": "Old title", "abstract": "Old abstract"}
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "translations.json"
            cache_path.write_text(json.dumps({
                article["doi"]: {"source_hash": "old-hash", "title_zh": "旧译文", "abstract_zh": "旧摘要"}
            }), encoding="utf-8")

            translated = translate_articles([article], cache_path)
            self.assertEqual(translated[article["doi"]], {"title": "", "abstract": ""})


if __name__ == "__main__":
    unittest.main()
