# Local Article Hiding Design

## Goal

Let a reader remove an irrelevant article from their own reading center without changing the shared static article data or other readers' views.

## Interaction

Add a `从我的阅读中心移除` action to the article detail view. Hidden articles are excluded from the normal `全部`, `待读`, `已读`, and `收藏` views. Add an `已隐藏` reading-state filter that lists hidden articles and offers `恢复显示` for each one.

## Data and scope

Store a boolean `hidden` flag in the existing browser-local record, keyed by the article DOI, URL, or title using the current stable-key logic. Hiding or restoring an article must preserve its existing read, favorite, and note fields. The feature is local to the current browser and site origin; it does not modify generated article data, affect other readers, or prevent the article from appearing in a future report after local storage is cleared or another browser/device is used.

## Boundaries

Keep the feature client-side and compatible with the static GitHub Pages site. Do not add a server endpoint, repository-wide exclusion list, permanent deletion, or synchronization across browsers. Keep hidden records available to the existing notes export.

## Verification

Verify that hiding removes an article from normal reading-state views, the hidden filter can show and restore it, and read/favorite/note data remains intact across hide and restore. Run relevant card tests and inspect the generated `docs/index.html` output.
