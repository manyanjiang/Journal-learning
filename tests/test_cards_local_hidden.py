import json
import re
import shutil
import subprocess
import unittest

from jalert.cards import build_html


class LocalArticleHidingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        if not cls.node:
            raise unittest.SkipTest("Node.js is required to exercise browser-local state helpers")
        cls.page = build_html([], [], [], project="Test", generated_at="2026-11-18 10:00")
        match = re.search(
            r"// LOCAL_HIDDEN_HELPERS_START\s*(.*?)\s*// LOCAL_HIDDEN_HELPERS_END",
            cls.page,
            re.DOTALL,
        )
        cls.helpers = match.group(1) if match else ""

    def run_helper(self, expression):
        script = (
            "const vm=require('node:vm');\n"
            f"vm.runInThisContext({json.dumps(self.helpers)});\n"
            f"process.stdout.write(JSON.stringify({expression}));\n"
        )
        result = subprocess.run(
            [self.node, "-e", script], text=True, capture_output=True,
            check=True, encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_hidden_filter_hides_from_normal_views_and_can_select_hidden_records(self):
        result = self.run_helper("({all:recordMatchesReadingState({hidden:true},'all'),unread:recordMatchesReadingState({hidden:true},'unread'),hidden:recordMatchesReadingState({hidden:true},'hidden'),visible:recordMatchesReadingState({read:true},'all')})")
        self.assertEqual(result, {"all": False, "unread": False, "hidden": True, "visible": True})

    def test_hide_and_restore_patches_preserve_read_favorite_and_note(self):
        result = self.run_helper("mergeArticleRecord({read:true,saved:true,note:'keep this'}, {hidden:true})")
        restored = self.run_helper("mergeArticleRecord({read:true,saved:true,note:'keep this',hidden:true}, {hidden:false})")
        self.assertEqual(result, {"read": True, "saved": True, "note": "keep this", "hidden": True})
        self.assertEqual(restored, {"read": True, "saved": True, "note": "keep this", "hidden": False})

    def test_page_exposes_hidden_filter_and_recoverable_modal_action(self):
        self.assertIn('data-state="hidden"', self.page)
        self.assertIn('id="mhide"', self.page)
        self.assertIn("从我的阅读中心移除", self.page)
        self.assertIn("恢复显示", self.page)

    def test_page_exposes_topic_jump_select_and_keeps_topic_tabs(self):
        self.assertIn('id="topic-jump"', self.page)
        self.assertIn('aria-label="跳转到主题"', self.page)
        self.assertIn('id="tabs"', self.page)
        self.assertIn("topicJump.onchange", self.page)
        self.assertIn("state.topic = d.k", self.page)


if __name__ == "__main__":
    unittest.main()
