import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "seen_articles.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_articles (
                id TEXT PRIMARY KEY,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            DELETE FROM seen_articles
            WHERE seen_at < datetime('now', '-30 days')
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                articles_fetched INTEGER DEFAULT 0,
                articles_new INTEGER DEFAULT 0,
                articles_classified INTEGER DEFAULT 0,
                articles_enriched INTEGER DEFAULT 0,
                articles_routed INTEGER DEFAULT 0,
                duration_seconds REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS article_events (
                article_id TEXT PRIMARY KEY,
                run_id INTEGER NOT NULL,
                feed_name TEXT,
                company_name TEXT,
                erp_likelihood INTEGER,
                erp_signals TEXT,
                in_tam_geography INTEGER,
                firmographics_score REAL,
                should_route INTEGER,
                exclusion_reason TEXT,
                hq_state TEXT,
                hq_country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("DELETE FROM pipeline_runs WHERE run_at < datetime('now', '-60 days')")
        conn.execute("DELETE FROM article_events WHERE created_at < datetime('now', '-60 days')")


def is_seen(article_id: str) -> bool:
    with _conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_articles WHERE id = ?", (article_id,)
        ).fetchone()
        return row is not None


def mark_seen(article_id: str):
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_articles (id) VALUES (?)", (article_id,)
        )


def start_run() -> int:
    with _conn() as conn:
        cur = conn.execute("INSERT INTO pipeline_runs (run_at) VALUES (CURRENT_TIMESTAMP)")
        return cur.lastrowid


def finish_run(
    run_id: int,
    fetched: int,
    new: int,
    classified: int,
    enriched: int,
    routed: int,
    duration: float,
):
    with _conn() as conn:
        conn.execute(
            """
            UPDATE pipeline_runs
            SET articles_fetched=?, articles_new=?, articles_classified=?,
                articles_enriched=?, articles_routed=?, duration_seconds=?
            WHERE id=?
            """,
            (fetched, new, classified, enriched, routed, round(duration, 2), run_id),
        )


def record_article_event(run_id: int, article: dict, result: dict):
    location = result.get("location") or {}
    enrichment = result.get("enrichment") or {}
    hq_state = location.get("state_or_province") or enrichment.get("hq_state_or_province")
    hq_country = location.get("country") or enrichment.get("hq_country")
    with _conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO article_events (
                article_id, run_id, feed_name, company_name,
                erp_likelihood, erp_signals, in_tam_geography,
                firmographics_score, should_route, exclusion_reason,
                hq_state, hq_country
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                article["id"],
                run_id,
                article.get("source"),
                result.get("company_name"),
                result.get("erp_likelihood"),
                json.dumps(result.get("erp_signals") or []),
                1 if result.get("in_tam_geography") else 0,
                result.get("firmographics_score"),
                1 if result.get("should_route") else 0,
                result.get("exclusion_reason"),
                hq_state,
                hq_country,
            ),
        )
