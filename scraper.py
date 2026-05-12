import calendar
import hashlib
import logging
import re
from datetime import datetime, timezone, timedelta

import feedparser
import requests

from config import RSS_FEEDS, MAX_ENTRIES_PER_FEED, MAX_ARTICLE_AGE_MINUTES

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ERPSignalBot/1.0)"}

logger = logging.getLogger(__name__)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s{2,}")


def _strip_html(text: str) -> str:
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def _article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _parse_published(entry) -> datetime | None:
    """Return a UTC-aware datetime from a feedparser entry, or None if unparseable."""
    pt = entry.get("published_parsed") or entry.get("updated_parsed")
    if pt:
        try:
            return datetime.fromtimestamp(calendar.timegm(pt), tz=timezone.utc)
        except Exception:
            pass
    return None


def _fetch_full_text(url: str) -> str:
    """Fetch full article body via newspaper3k. Returns empty string on any failure."""
    try:
        from newspaper import Article
        art = Article(url, request_timeout=8)
        art.download()
        art.parse()
        return art.text.strip()
    except Exception:
        return ""


def fetch_new_articles() -> list[dict]:
    """Fetch entries from all configured RSS feeds published within MAX_ARTICLE_AGE_MINUTES."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=MAX_ARTICLE_AGE_MINUTES)
    articles = []
    skipped_old = 0

    for feed_cfg in RSS_FEEDS:
        try:
            resp = requests.get(feed_cfg["url"], headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            entries = feed.entries[:MAX_ENTRIES_PER_FEED]

            feed_new = 0
            for entry in entries:
                url = entry.get("link") or entry.get("id") or ""
                if not url:
                    continue

                # Date filter — skip anything older than the cutoff
                pub_dt = _parse_published(entry)
                if pub_dt is not None and pub_dt < cutoff:
                    skipped_old += 1
                    continue

                content_raw = (
                    entry.get("summary")
                    or entry.get("description")
                    or ""
                )
                if not content_raw and entry.get("content"):
                    content_raw = entry["content"][0].get("value", "")

                rss_content = _strip_html(content_raw)
                full_text = _fetch_full_text(url)
                content = (full_text if len(full_text) > len(rss_content) else rss_content)[:4000]
                pub_str = pub_dt.strftime("%Y-%m-%d %H:%M UTC") if pub_dt else entry.get("published", "unknown")

                articles.append({
                    "id": _article_id(url),
                    "title": _strip_html(entry.get("title", "")),
                    "url": url,
                    "content": content,
                    "source": feed_cfg["name"],
                    "published": pub_str,
                    "published_dt": pub_dt,
                })
                feed_new += 1

            logger.info(f"[{feed_cfg['name']}] {feed_new} recent articles (of {len(entries)} in feed)")

        except Exception:
            logger.exception(f"[{feed_cfg['name']}] error fetching feed")

    if skipped_old:
        logger.info(f"Skipped {skipped_old} articles older than {MAX_ARTICLE_AGE_MINUTES} minutes")

    return articles
