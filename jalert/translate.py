"""DeepL translation cache for article card previews."""

from __future__ import annotations

import hashlib
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://api-free.deepl.com/v2/translate"


def article_key(article: dict) -> str:
    return str(article.get("doi") or article.get("url") or article.get("title") or "").lower()


def _source(article: dict, summary_chars: int) -> tuple[str, str, str]:
    title = str(article.get("title") or "").strip()
    abstract = " ".join(str(article.get("abstract") or "").split())[:summary_chars]
    digest = hashlib.sha256((title + "\n" + abstract).encode("utf-8")).hexdigest()
    return title, abstract, digest


def translate_articles(
    articles: list[dict], cache_path: Path, *, api_key: str = "",
    summary_chars: int = 320, api_url: str = API_URL,
    log: logging.Logger | None = None,
) -> dict[str, dict[str, str]]:
    """Translate missing/changed title and short abstract fields, retaining a JSON cache."""
    logger = log or logging.getLogger(__name__)
    cache_path = Path(cache_path)
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    except (OSError, json.JSONDecodeError):
        logger.warning("translation cache could not be read; rebuilding it")
        cache = {}

    if not isinstance(cache, dict):
        cache = {}
    pending = []
    sources = {}
    for article in articles:
        key = article_key(article)
        if not key:
            continue
        title, abstract, digest = _source(article, summary_chars)
        sources[key] = (title, abstract, digest)
        saved = cache.get(key) or {}
        if saved.get("source_hash") != digest or not saved.get("title_zh"):
            pending.append((key, title, abstract, digest))

    if pending and not api_key:
        logger.info("DeepL skipped: DEEPL_AUTH_KEY is not configured (%d article(s) need translation)",
                    len(pending))

    changed = False
    if api_key and pending:
        requests = []
        for key, title, abstract, digest in pending:
            requests.append((key, "title_zh", title, digest))
            if abstract:
                requests.append((key, "abstract_zh", abstract, digest))

        translated = 0
        for start in range(0, len(requests), 40):
            batch = requests[start:start + 40]
            fields = [("text", item[2]) for item in batch]
            fields.extend((("source_lang", "EN"), ("target_lang", "ZH")))
            data = urllib.parse.urlencode(fields).encode("utf-8")
            request = urllib.request.Request(
                api_url,
                data=data,
                headers={"Authorization": f"DeepL-Auth-Key {api_key}",
                         "Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    result = json.loads(response.read().decode("utf-8"))
                outputs = result.get("translations") or []
                if len(outputs) != len(batch):
                    raise ValueError("DeepL response count did not match request")
            except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
                logger.warning("DeepL translation failed; keeping source text: %s", str(exc)[:180])
                break

            for item, output in zip(batch, outputs):
                key, field, _text, digest = item
                record = cache.setdefault(key, {"source_hash": digest})
                if record.get("source_hash") != digest:
                    record.clear()
                    record["source_hash"] = digest
                record[field] = str(output.get("text") or "").strip()
                translated += 1
            changed = True

        if translated:
            logger.info("DeepL translated %d text field(s) for %d article(s)",
                        translated, len(pending))

    if changed:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = cache_path.with_suffix(cache_path.suffix + ".tmp")
        temporary.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(cache_path)

    output = {}
    for key, (_title, _abstract, digest) in sources.items():
        saved = cache.get(key) or {}
        valid = saved.get("source_hash") == digest
        output[key] = {
            "title": str(saved.get("title_zh") or "") if valid else "",
            "abstract": str(saved.get("abstract_zh") or "") if valid else "",
        }
    return output
