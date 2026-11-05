import json
import re
import shutil
import subprocess
import unittest

from jalert.cards import build_html


class CardRisExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        if not cls.node:
            raise unittest.SkipTest("Node.js is required to exercise the browser RIS serializer")
        page = build_html([], [], [], project="Test", generated_at="2026-11-05 10:00")
        match = re.search(
            r"// RIS_EXPORT_HELPERS_START\s*(.*?)\s*// RIS_EXPORT_HELPERS_END",
            page,
            re.DOTALL,
        )
        if not match:
            cls.helpers = ""
        else:
            cls.helpers = match.group(1)

    def serialize(self, article):
        script = (
            "const vm=require('node:vm');\n"
            "const input=JSON.parse(require('node:fs').readFileSync(0,'utf8'));\n"
            f"vm.runInThisContext({json.dumps(self.helpers)});\n"
            "process.stdout.write(JSON.stringify(buildRis(input)));\n"
        )
        result = subprocess.run(
            [self.node, "-e", script], input=json.dumps(article), text=True,
            capture_output=True, check=True, encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_exports_only_present_source_fields_and_each_recorded_author(self):
        article = {
            "title": "Original title",
            "authors": ["Alpha, A.", "Beta, B."],
            "journal": "Journal of Tests",
            "pubdate": "2025-07-18",
            "doi": "10.1000/example",
            "abstract": "Original abstract",
            "url": "https://example.org/paper",
        }
        ris = self.serialize(article)
        self.assertEqual(
            ris,
            "TY  - JOUR\r\nTI  - Original title\r\nAU  - Alpha, A.\r\n"
            "AU  - Beta, B.\r\nJF  - Journal of Tests\r\nPY  - 2025\r\n"
            "DO  - 10.1000/example\r\nAB  - Original abstract\r\n"
            "UR  - https://example.org/paper\r\nER  - \r\n",
        )

    def test_omits_missing_fields_and_sanitizes_newlines_without_inventing_data(self):
        ris = self.serialize({"title": "First line\nER  - injected", "authors": []})
        self.assertIn("TI  - First line ER  - injected\r\n", ris)
        self.assertNotIn("AU  -", ris)
        self.assertNotIn("JF  -", ris)
        self.assertNotIn("PY  -", ris)
        self.assertNotIn("DO  -", ris)
        self.assertNotIn("AB  -", ris)
        self.assertNotIn("UR  -", ris)
        self.assertTrue(ris.endswith("ER  - \r\n"))

    def test_omits_abstract_that_the_daily_report_marked_as_truncated(self):
        ris = self.serialize({
            "title": "Source title",
            "abstract": "Only the first part …",
            "abstractTruncated": True,
        })
        self.assertNotIn("AB  -", ris)
        self.assertIn("TI  - Source title\r\n", ris)

    def test_uses_a_safe_doi_based_filename(self):
        script = (
            "const vm=require('node:vm');\n"
            f"vm.runInThisContext({json.dumps(self.helpers)});\n"
            "process.stdout.write(risFilename(JSON.parse(process.argv[1])));\n"
        )
        result = subprocess.run(
            [self.node, "-e", script, json.dumps({"doi": "10.1038/a:b"})],
            text=True, capture_output=True, check=True, encoding="utf-8",
        )
        self.assertEqual(result.stdout, "10.1038_a_b.ris")

    def test_modal_places_ris_download_with_read_and_favorite_actions(self):
        page = build_html([], [], [], project="Test", generated_at="2026-11-05 10:00")
        actions = re.search(r'<div class="personal-actions">(.*?)</div>', page, re.DOTALL)
        self.assertIsNotNone(actions)
        self.assertIn('id="mread"', actions.group(1))
        self.assertIn('id="msave"', actions.group(1))
        self.assertIn('id="mris"', actions.group(1))
        self.assertIn("下载 RIS", actions.group(1))


class ReadingNotesExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        if not cls.node:
            raise unittest.SkipTest("Node.js is required to exercise the browser notes serializer")
        page = build_html([], [], [], project="Test", generated_at="2026-11-05 10:00")
        match = re.search(
            r"// NOTES_EXPORT_HELPERS_START\s*(.*?)\s*// NOTES_EXPORT_HELPERS_END",
            page,
            re.DOTALL,
        )
        cls.helpers = match.group(1) if match else ""
        cls.page = page

    def export_markdown(self, articles, records):
        script = (
            "const vm=require('node:vm');\n"
            "const input=JSON.parse(require('node:fs').readFileSync(0,'utf8'));\n"
            f"vm.runInThisContext({json.dumps(self.helpers)});\n"
            "process.stdout.write(JSON.stringify(buildNotesMarkdown(input.articles,input.records)));\n"
        )
        result = subprocess.run(
            [self.node, "-e", script],
            input=json.dumps({"articles": articles, "records": records}),
            text=True, capture_output=True, check=True, encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_exports_nonempty_notes_with_article_metadata_and_excludes_empty_records(self):
        articles = [
            {
                "title": "Carbon pathways",
                "authors": ["Lin, A.", "Chen, B."],
                "journal": "Nature Energy",
                "pubdate": "2026-10-31",
                "doi": "10.1000/carbon",
                "url": "https://example.org/carbon",
                "topics": ["CCUS", "能源转型"],
            },
            {"title": "No note", "doi": "10.1000/empty", "url": "https://example.org/empty"},
        ]
        records = {
            "10.1000/carbon": {"note": "方法值得复用\n需要核对边界条件", "read": True, "saved": True},
            "10.1000/empty": {"note": "  ", "read": True},
        }
        markdown = self.export_markdown(articles, records)
        self.assertIn("# 文献阅读笔记", markdown)
        self.assertIn("共 1 篇", markdown)
        self.assertIn("## 1. Carbon pathways", markdown)
        self.assertIn("作者：Lin, A.; Chen, B.", markdown)
        self.assertIn("期刊：Nature Energy", markdown)
        self.assertIn("发表日期：2026-10-31", markdown)
        self.assertIn("DOI：10.1000/carbon", markdown)
        self.assertIn("原文链接：https://example.org/carbon", markdown)
        self.assertIn("关注方向：CCUS / 能源转型", markdown)
        self.assertIn("> 方法值得复用\n> 需要核对边界条件", markdown)
        self.assertNotIn("No note", markdown)

    def test_places_notes_export_button_next_to_sort_controls(self):
        controls = re.search(r'<div class="seg" id="sortseg">(.*?)</div>(.*?)<div class="count"', self.page, re.DOTALL)
        self.assertIsNotNone(controls)
        self.assertIn('id="export-notes"', controls.group(2))
        self.assertIn("导出笔记", controls.group(2))

    def test_updates_export_button_count_when_a_note_is_saved(self):
        self.assertIn("id=\"note-count\"", self.page)
        self.assertIn("updateNotesExportButton()", self.page)
        self.assertIn("articleSnapshot(a)", self.page)

    def test_exports_notes_for_articles_that_have_left_the_current_page(self):
        markdown = self.export_markdown([], {
            "10.1000/archived": {
                "note": "保留长期比较",
                "article": {
                    "title": "Archived study",
                    "journal": "One Earth",
                    "pubdate": "2025-03-01",
                    "doi": "10.1000/archived",
                    "url": "https://example.org/archived",
                },
            },
        })
        self.assertIn("## 1. Archived study", markdown)
        self.assertIn("期刊：One Earth", markdown)
        self.assertIn("> 保留长期比较", markdown)


if __name__ == "__main__":
    unittest.main()
