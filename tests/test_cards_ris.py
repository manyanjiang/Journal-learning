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
            capture_output=True, check=True,
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

    def test_modal_places_ris_download_with_read_and_favorite_actions(self):
        page = build_html([], [], [], project="Test", generated_at="2026-11-05 10:00")
        actions = re.search(r'<div class="personal-actions">(.*?)</div>', page, re.DOTALL)
        self.assertIsNotNone(actions)
        self.assertIn('id="mread"', actions.group(1))
        self.assertIn('id="msave"', actions.group(1))
        self.assertIn('id="mris"', actions.group(1))
        self.assertIn("下载 RIS", actions.group(1))


if __name__ == "__main__":
    unittest.main()
