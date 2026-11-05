# RIS Export Design

## Goal

Allow a reader to download an EndNote-compatible RIS citation for one paper from its article detail view.

## Interaction

Add one `下载 RIS` button beside the existing read and favorite actions. Activating it downloads a `.ris` file for the currently open article without changing its read, favorite, or note state.

## Data and accuracy

Export only bibliographic fields already present on that article card and sourced from the publication feeds or bibliographic APIs. Do not translate, infer, or synthesize citation fields. Omit unavailable fields. Escape RIS delimiters and line breaks so user-facing text cannot corrupt the record. Use UTF-8 text with CRLF line endings and a final `ER  -` record terminator.

Map available values to RIS fields: `TY` journal article, `TI` title, repeated `AU` authors, `JF` journal, `PY` publication year parsed from the recorded publication date, `DO` DOI, `AB` abstract, `UR` article URL, and `ER` record end. Only include a tag when its source value exists; use the recorded title as-is and do not construct a DOI URL when the article URL is absent. Daily reports explicitly mark abstracts shortened at 700 characters with a trailing ` …`; omit `AB` for those cards so a partial excerpt is not represented as a complete abstract.

## Boundaries

The feature is client-side and works with the static GitHub Pages site. It exports one record per click. Batch export, EndNote integration, metadata lookups at download time, and changes to notifications are out of scope.

## Verification

Check that generated RIS includes only present source fields, preserves multiple authors as repeated `AU` tags, safely escapes special characters and newlines, downloads with a stable `.ris` filename, and leaves existing read/favorite/note behavior intact. Run the repository test suite and inspect the generated card page.
