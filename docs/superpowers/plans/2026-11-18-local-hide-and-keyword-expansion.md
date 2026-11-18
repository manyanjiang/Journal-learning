# Local Hiding and Keyword Expansion Implementation Plan

> **For agentic workers:** Implement the checked steps in order. The user approved inline execution in this session.

**Goal:** Add recoverable browser-local article hiding and expand the configured research topics and terms.

**Architecture:** Keep the static site and existing `journal-alert-library-v1` local record store. Store a `hidden` flag alongside existing per-article state, filter hidden articles into an `已隐藏` view, and preserve notes/read/favorite fields. Update only configured keyword groups, then regenerate the static card wall from existing reports.

**Tech Stack:** Python 3 standard library, JSON config, generated HTML/JavaScript, unittest, Node.js for browser-side helper checks.

## Global Constraints

- Hidden state is local to the current browser and must not modify shared article data.
- Hiding/restoring must preserve read, saved, and note values.
- BECCS belongs only to `CDR碳移除与负排放`.
- Do not add bare `hydrogen`, `ammonia`, `methanol`, `enhanced oil recovery`, or `enhanced gas recovery` terms.
- Do not change journal sources, scoring logic, historical reports, or secret configuration.

---

### Task 1: Expand research keyword configuration

**Files:**
- Modify: `config.json`
- Test: `tests/test_keyword_config.py`

- [x] Add the two approved topic groups and the agreed terms to the existing groups, preserving existing labels and terms.
- [x] Add tests that parse JSON, assert unique labels and per-group terms, check the approved new phrases, verify BECCS is only in the CDR group, and ensure the excluded bare terms are absent.
- [x] Run `python -m unittest tests.test_keyword_config -v`.

### Task 2: Add recoverable local article hiding

**Files:**
- Modify: `jalert/cards.py`
- Test: `tests/test_cards_local_hidden.py`

- [x] Add an `已隐藏` state filter and make normal states omit hidden records while the hidden state selects them.
- [x] Add a detail action that toggles `hidden` without replacing other record fields; label it `从我的阅读中心移除` or `恢复显示` based on current state.
- [x] Add browser-helper tests for state filtering and preservation of `read`, `saved`, and `note`, plus a rendered modal/control assertion.
- [x] Run `python -m unittest tests.test_cards_local_hidden tests.test_cards_ris tests.test_cards_filter -v`.

### Task 3: Regenerate and verify the reading center

**Files:**
- Regenerate: `docs/index.html`

- [x] Run `python -m jalert.cards --reports reports --out docs/index.html --config config.json --project 个人文献中心`.
- [x] Run `python -m unittest discover -s tests -v`.
- [x] Confirm generated topic navigation includes both new labels, generated HTML contains hide/restore controls and the hidden state, and `git diff --check` passes.
