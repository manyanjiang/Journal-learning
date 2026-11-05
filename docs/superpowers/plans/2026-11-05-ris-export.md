# Article RIS Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single-article RIS download action to each article detail modal.

**Architecture:** Keep the generated site self-contained. Add a small browser-side RIS serializer using only card data already embedded in `docs/index.html`, then download it as a UTF-8 `.ris` Blob. Test the serializer's emitted behavior and the placement of its action in the card page.

**Tech Stack:** Python standard library, generated HTML, browser JavaScript, `unittest`.

## Global Constraints

- Export only source fields already present in the article card; never translate, infer, or synthesize values.
- Omit missing fields; the download must still work.
- Preserve existing read, favorite, note, and source-link interactions.
- Keep the page self-contained with no new runtime dependencies or external requests.

---

### Task 1: Add and test the RIS serializer

**Files:**
- Modify: `jalert/cards.py` inline detail-modal JavaScript
- Create: `tests/test_cards_ris.py`

**Interfaces:**
- Browser helper: `risField(tag, value)` emits one escaped RIS field or an empty string for a missing value.
- Browser helper: `buildRis(article)` emits one CRLF-delimited RIS journal-article record ending in `ER  -`.

- [ ] **Step 1: Write failing tests**

Add tests that extract the named helper source from `build_html` and exercise it in a minimal JavaScript runtime where available, or inspect generated page output for a serializer that consumes `title`, each `authors` entry, `journal`, the year from `pubdate`, `doi`, `abstract`, and `url`. Verify line breaks and backslashes in field values are escaped, absent values are omitted, repeated author fields are retained, and the modal contains one `下载 RIS` action next to read/favorite actions.

- [ ] **Step 2: Run focused tests and confirm they fail for missing RIS behavior**

Run: `python -m unittest tests.test_cards_ris -v`

- [ ] **Step 3: Implement the serializer and download handler**

Build fields only from present properties. Escape backslash, CR, LF, and RIS delimiter characters; use UTF-8 Blob bytes and CRLF separators. Add an `id="mris"` button beside `mread` and `msave`. On activation, create an object URL, trigger download with a sanitized DOI-or-title `.ris` filename, then revoke the URL.

- [ ] **Step 4: Run focused and full tests**

Run: `python -m unittest tests.test_cards_ris -v`

Run: `python -m unittest discover -s tests -v`

- [ ] **Step 5: Rebuild and inspect the static page**

Run: `python run.py --cards`

Verify `docs/index.html` includes the RIS action and that its article data fields are passed without adding synthesized metadata.

- [ ] **Step 6: Commit the feature**

Commit only `jalert/cards.py`, `tests/test_cards_ris.py`, and the regenerated `docs/index.html` with message `Add per-article RIS export`.
