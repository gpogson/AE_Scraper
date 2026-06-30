import json
import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras


def _db_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    # psycopg2 requires postgresql://, Railway provides postgres://
    return url.replace("postgres://", "postgresql://", 1) if url.startswith("postgres://") else url


@contextmanager
def _conn():
    conn = psycopg2.connect(_db_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS seen_articles (
                    id TEXT PRIMARY KEY,
                    seen_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id SERIAL PRIMARY KEY,
                    run_at TIMESTAMP DEFAULT NOW(),
                    articles_fetched INTEGER DEFAULT 0,
                    articles_new INTEGER DEFAULT 0,
                    articles_classified INTEGER DEFAULT 0,
                    articles_enriched INTEGER DEFAULT 0,
                    articles_routed INTEGER DEFAULT 0,
                    duration_seconds REAL
                )
            """)
            cur.execute("""
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
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS company_cache (
                    company_key TEXT PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            # Prune old analytics data
            cur.execute("DELETE FROM seen_articles WHERE seen_at < NOW() - INTERVAL '30 days'")
            cur.execute("DELETE FROM pipeline_runs WHERE run_at < NOW() - INTERVAL '60 days'")
            cur.execute("DELETE FROM article_events WHERE created_at < NOW() - INTERVAL '60 days'")


def is_seen(article_id: str) -> bool:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM seen_articles WHERE id = %s", (article_id,))
            return cur.fetchone() is not None


def mark_seen(article_id: str):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO seen_articles (id) VALUES (%s) ON CONFLICT DO NOTHING",
                (article_id,),
            )


def start_run() -> int:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO pipeline_runs (run_at) VALUES (NOW()) RETURNING id")
            return cur.fetchone()[0]


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
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pipeline_runs
                SET articles_fetched=%s, articles_new=%s, articles_classified=%s,
                    articles_enriched=%s, articles_routed=%s, duration_seconds=%s
                WHERE id=%s
                """,
                (fetched, new, classified, enriched, routed, round(duration, 2), run_id),
            )


def record_article_event(run_id: int, article: dict, result: dict):
    location = result.get("location") or {}
    enrichment = result.get("enrichment") or {}
    hq_state = location.get("state_or_province") or enrichment.get("hq_state_or_province")
    hq_country = location.get("country") or enrichment.get("hq_country")
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO article_events (
                    article_id, run_id, feed_name, company_name,
                    erp_likelihood, erp_signals, in_tam_geography,
                    firmographics_score, should_route, exclusion_reason,
                    hq_state, hq_country
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (article_id) DO NOTHING
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


def get_cached_company(company_key: str) -> dict | None:
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT data FROM company_cache WHERE company_key = %s", (company_key,))
            row = cur.fetchone()
            return dict(row["data"]) if row else None


def set_cached_company(company_key: str, data: dict):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO company_cache (company_key, data) VALUES (%s, %s)
                ON CONFLICT (company_key) DO UPDATE SET data = EXCLUDED.data
                """,
                (company_key, json.dumps(data)),
            )
