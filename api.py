import csv
import io
import json
import os
import secrets
from contextlib import contextmanager
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from config import ERP_SIGNALS

load_dotenv()

app = FastAPI(docs_url=None, redoc_url=None)
security = HTTPBasic()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

_WINDOW_HOURS = {"24h": 24, "7d": 168, "30d": 720}


def _db_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    return url.replace("postgres://", "postgresql://", 1) if url.startswith("postgres://") else url


@contextmanager
def _conn():
    conn = psycopg2.connect(_db_url())
    try:
        yield conn
    finally:
        conn.close()


def _wc(window: str) -> str:
    hours = _WINDOW_HOURS.get(window, 24)
    return f"NOW() - INTERVAL '{hours} hours'"


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    expected_pass = os.environ.get("DASHBOARD_PASSWORD", "erpsignals")
    ok = secrets.compare_digest(credentials.username.encode(), b"admin") and secrets.compare_digest(
        credentials.password.encode(), expected_pass.encode()
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.on_event("startup")
async def startup():
    from db import init_db
    init_db()


@app.get("/", response_class=HTMLResponse)
async def leads_page(request: Request, _: None = Depends(check_auth)):
    return templates.TemplateResponse(request, "leads.html")


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request, _: None = Depends(check_auth)):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/api/signal-tags")
async def get_signal_tags(_: None = Depends(check_auth)):
    return ERP_SIGNALS


def _lead_filters(search: str, signal: str, window: str) -> tuple[str, list]:
    conditions = ["should_route = 1"]
    params: list = []

    if window != "all":
        conditions.append(f"created_at >= {_wc(window)}")
    if search:
        conditions.append("company_name ILIKE %s")
        params.append(f"%{search}%")
    if signal:
        conditions.append("erp_signals LIKE %s")
        params.append(f'%"{signal}"%')

    return " AND ".join(conditions), params


@app.get("/api/leads")
async def get_leads(
    search: str = "",
    signal: str = "",
    window: str = "all",
    limit: int = 50,
    offset: int = 0,
    _: None = Depends(check_auth),
):
    where_clause, params = _lead_filters(search, signal, window)

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM article_events WHERE {where_clause}", params)
            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT company_name, article_url, article_title, website,
                       erp_likelihood, firmographics_score, erp_signals,
                       hq_state, hq_country, employee_count, estimated_revenue,
                       industry, signal_summary, feed_name, created_at
                FROM article_events
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

    items = []
    for r in rows:
        d = dict(r)
        d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
        try:
            d["erp_signals"] = json.loads(d["erp_signals"] or "[]")
        except (json.JSONDecodeError, TypeError):
            d["erp_signals"] = []
        items.append(d)

    return {"total": total, "items": items}


@app.get("/api/leads/export.csv")
async def export_leads_csv(
    search: str = "",
    signal: str = "",
    window: str = "all",
    _: None = Depends(check_auth),
):
    where_clause, params = _lead_filters(search, signal, window)

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT company_name, COALESCE(website, article_url) AS company_url,
                       article_url, erp_likelihood, firmographics_score, erp_signals,
                       hq_state, hq_country, employee_count, estimated_revenue,
                       industry, created_at
                FROM article_events
                WHERE {where_clause}
                ORDER BY created_at DESC
                """,
                params,
            )
            rows = cur.fetchall()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Company Name", "Company URL", "Article URL", "ERP Likelihood",
        "Firmographics Score", "Signals", "State", "Country",
        "Employees", "Revenue", "Industry", "Date",
    ])
    for r in rows:
        try:
            signals = ", ".join(json.loads(r["erp_signals"] or "[]"))
        except (json.JSONDecodeError, TypeError):
            signals = ""
        writer.writerow([
            r["company_name"], r["company_url"], r["article_url"],
            r["erp_likelihood"], r["firmographics_score"], signals,
            r["hq_state"], r["hq_country"], r["employee_count"],
            r["estimated_revenue"], r["industry"],
            r["created_at"].strftime("%Y-%m-%d %H:%M") if r["created_at"] else "",
        ])
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=erp_leads.csv"},
    )


@app.get("/api/stats")
async def get_stats(window: str = "24h", _: None = Depends(check_auth)):
    wc = _wc(window)
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT
                    COUNT(*) AS run_count,
                    COALESCE(SUM(articles_fetched), 0) AS fetched,
                    COALESCE(SUM(articles_new), 0) AS new_arts,
                    COALESCE(SUM(articles_classified), 0) AS classified,
                    COALESCE(SUM(articles_enriched), 0) AS enriched,
                    COALESCE(SUM(articles_routed), 0) AS routed,
                    MAX(run_at) AS last_run,
                    COALESCE(AVG(duration_seconds), 0) AS avg_duration
                FROM pipeline_runs
                WHERE run_at >= {wc}
            """)
            r = cur.fetchone()

    fetched    = int(r["fetched"] or 0)
    new_arts   = int(r["new_arts"] or 0)
    classified = int(r["classified"] or 0)
    enriched   = int(r["enriched"] or 0)
    routed     = int(r["routed"] or 0)
    last_run   = r["last_run"].isoformat() if r["last_run"] else None

    return {
        "window": window,
        "run_count": int(r["run_count"]),
        "articles_fetched": fetched,
        "articles_new": new_arts,
        "articles_classified": classified,
        "articles_enriched": enriched,
        "articles_routed": routed,
        "new_rate": round(new_arts / fetched * 100, 1) if fetched else 0,
        "classification_rate": round(classified / new_arts * 100, 1) if new_arts else 0,
        "enrichment_rate": round(enriched / classified * 100, 1) if classified else 0,
        "routing_rate": round(routed / fetched * 100, 2) if fetched else 0,
        "last_run_at": last_run,
        "avg_duration_seconds": round(float(r["avg_duration"] or 0), 1),
    }


@app.get("/api/runs")
async def get_runs(limit: int = 25, _: None = Depends(check_auth)):
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, run_at, articles_fetched, articles_new, articles_classified,
                       articles_enriched, articles_routed, duration_seconds
                FROM pipeline_runs
                ORDER BY run_at DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
    return [
        {**dict(r), "run_at": r["run_at"].isoformat() if r["run_at"] else None}
        for r in rows
    ]


@app.get("/api/feeds")
async def get_feeds(window: str = "24h", _: None = Depends(check_auth)):
    wc = _wc(window)
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT
                    feed_name,
                    COUNT(*) AS classified,
                    SUM(CASE WHEN erp_likelihood >= 7 THEN 1 ELSE 0 END) AS with_signal,
                    SUM(should_route) AS routed,
                    ROUND(AVG(erp_likelihood)::numeric, 1) AS avg_likelihood
                FROM article_events
                WHERE created_at >= {wc} AND feed_name IS NOT NULL
                GROUP BY feed_name
                ORDER BY classified DESC
            """)
            rows = cur.fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["hit_rate"] = round(int(d["routed"]) / int(d["classified"]) * 100, 1) if d["classified"] else 0
        result.append(d)
    return result


@app.get("/api/signals")
async def get_signals(window: str = "24h", _: None = Depends(check_auth)):
    wc = _wc(window)
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT erp_signals FROM article_events
                WHERE created_at >= {wc} AND erp_signals IS NOT NULL
            """)
            rows = cur.fetchall()

    counts: dict[str, int] = {}
    for (signals_json,) in rows:
        try:
            for s in json.loads(signals_json):
                counts[s] = counts.get(s, 0) + 1
        except (json.JSONDecodeError, TypeError):
            pass

    return [{"signal": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]


@app.get("/api/activity")
async def get_activity(_: None = Depends(check_auth)):
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    to_char(date_trunc('hour', run_at), 'YYYY-MM-DD"T"HH24:00') AS hour,
                    SUM(articles_fetched) AS fetched,
                    SUM(articles_new) AS new_arts,
                    SUM(articles_routed) AS routed
                FROM pipeline_runs
                WHERE run_at >= NOW() - INTERVAL '24 hours'
                GROUP BY date_trunc('hour', run_at)
                ORDER BY date_trunc('hour', run_at)
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/routed")
async def get_routed(window: str = "24h", limit: int = 25, _: None = Depends(check_auth)):
    wc = _wc(window)
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT company_name, feed_name, erp_likelihood, firmographics_score,
                       erp_signals, hq_state, hq_country, exclusion_reason, created_at
                FROM article_events
                WHERE should_route = 1 AND created_at >= {wc}
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()

    result = []
    for r in rows:
        d = dict(r)
        d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
        try:
            d["erp_signals"] = json.loads(d["erp_signals"] or "[]")
        except (json.JSONDecodeError, TypeError):
            d["erp_signals"] = []
        result.append(d)
    return result


@app.get("/api/exclusions")
async def get_exclusions(window: str = "24h", _: None = Depends(check_auth)):
    wc = _wc(window)
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT exclusion_reason, COUNT(*) AS count
                FROM article_events
                WHERE exclusion_reason IS NOT NULL AND created_at >= {wc}
                GROUP BY exclusion_reason
                ORDER BY count DESC
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
