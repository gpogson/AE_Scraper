import json
import logging
import os

import requests

from config import TAM_US_STATES, TAM_CA_PROVINCES

logger = logging.getLogger(__name__)

# In-memory L1 cache (within process lifetime)
_memory_cache: dict = {}


# ---------------------------------------------------------------------------
# Serper.dev — broad Google search for company firmographics
# ---------------------------------------------------------------------------

def _serper_search(company_name: str) -> str:
    """
    Search Google via Serper for company revenue, employees, and website.
    Returns concatenated snippets from top 10 results + Knowledge Graph.
    """
    api_key = os.environ.get("SERPER_API_KEY", "")
    if not api_key:
        logger.warning("SERPER_API_KEY not set — skipping enrichment")
        return ""

    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            json={"q": f'"{company_name}" company revenue employees website', "num": 10},
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return ""

        data = resp.json()
        parts = []

        # Knowledge Graph — best structured data when Google recognizes the company
        kg = data.get("knowledgeGraph", {})
        if kg:
            parts.append(f"{kg.get('title', '')} — {kg.get('description', '')}")
            for attr, val in kg.get("attributes", {}).items():
                parts.append(f"{attr}: {val}")

        # Top 10 organic result snippets
        for r in data.get("organic", []):
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            if snippet:
                parts.append(f"{title}: {snippet}")

        return "\n".join(parts)

    except Exception:
        logger.debug(f"Serper search failed for: {company_name}")
    return ""


# ---------------------------------------------------------------------------
# GPT extraction
# ---------------------------------------------------------------------------

_ESTIMATE_FROM_ARTICLE_PROMPT = """Extract what you can about "{company_name}" from this press release.

Article:
{article_content}

Pull location from datelines (e.g. "SEATTLE, WA —"), HQ mentions, or where the company operates.
Estimate revenue and headcount from funding size, facility scale, growth language, and industry norms.
Prefix estimates with "est." — never return null for numeric fields.

Reply ONLY with this JSON:
{{
  "hq_city": "string or null",
  "hq_state_or_province": "2-letter code or null",
  "hq_country": "US or Canada or other or null",
  "employee_count": "string",
  "employee_count_est": <integer>,
  "estimated_revenue": "string",
  "revenue_millions_est": <float>,
  "website": "string or null",
  "industry": "string or null"
}}"""


_EXTRACT_PROMPT = """You are extracting firmographic data about "{company_name}" from these Google search results.

Search results:
{snippet}

Rules — you MUST always return a number, never null or unknown:
- employee_count: exact string if found e.g. "42", "50-200". If not found, estimate from revenue, industry, or company stage and prefix with "est."
- employee_count_est: integer best-estimate (midpoint if range). Default to 25 if no data at all.
- estimated_revenue: exact string if found e.g. "$8M". If not found, estimate from headcount or funding and prefix with "est."
- revenue_millions_est: float best-estimate in millions. Default to 3.0 if no data at all.
- website: the company's official homepage URL (not LinkedIn, not news articles). Extract from search results.
- hq_city, hq_state_or_province (2-letter code), hq_country ("US", "Canada", or "other")
- industry: one-line description

Reply ONLY with this JSON:
{{
  "hq_city": "string or null",
  "hq_state_or_province": "2-letter code or null",
  "hq_country": "US or Canada or other or null",
  "employee_count": "string",
  "employee_count_est": <integer>,
  "estimated_revenue": "string",
  "revenue_millions_est": <float>,
  "website": "string or null",
  "industry": "string or null"
}}"""


def _estimate_from_article(company_name: str, article_content: str) -> dict | None:
    """Estimate firmographics from article text when Serper returns nothing."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": _ESTIMATE_FROM_ARTICLE_PROMPT.format(
                company_name=company_name,
                article_content=article_content[:3000],
            )}],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=200,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        logger.debug(f"Article-based estimation failed for: {company_name}")
        return None


def _extract_with_gpt(company_name: str, snippet: str) -> dict | None:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": _EXTRACT_PROMPT.format(
                company_name=company_name,
                snippet=snippet,
            )}],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=200,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        logger.exception(f"GPT extraction failed for: {company_name}")
        return None


# ---------------------------------------------------------------------------
# Firmographics scoring
# ---------------------------------------------------------------------------

_ROUTE_THRESHOLD = 7   # erp_likelihood must be >= this to route
_MAX_EMPLOYEES   = 150
_MAX_REVENUE_M   = 80.0


def _firmographics_score(enrichment: dict) -> tuple[float, str | None]:
    """
    Score 0.0–10.0 based on how well the company fits the target profile.
    Returns (score, exclusion_reason).

    Employee component (0–5 pts):
      10–50   → 5.0  sweet spot
      51–100  → 4.5
      101–150 → 3.5
      <10     → 3.0
      unknown → 3.5
      >150    → EXCLUDED

    Revenue component (0–5 pts):
      $1M–$15M  → 5.0
      $15M–$30M → 4.0
      $30M–$50M → 3.0
      $50M–$80M → 2.0
      <$1M      → 2.5
      unknown   → 3.5
      >$80M     → EXCLUDED
    """
    emp = enrichment.get("employee_count_est")
    rev = enrichment.get("revenue_millions_est")

    if emp is not None and emp > _MAX_EMPLOYEES:
        return 0.0, f"employee count too high (~{emp})"
    if rev is not None and rev > _MAX_REVENUE_M:
        return 0.0, f"revenue too high (~${rev:.0f}M)"

    if emp is None:
        emp_score = 3.5
    elif emp <= 9:
        emp_score = 3.0
    elif emp <= 50:
        emp_score = 5.0
    elif emp <= 100:
        emp_score = 4.5
    else:
        emp_score = 3.5

    if rev is None:
        rev_score = 3.5
    elif rev < 1:
        rev_score = 2.5
    elif rev <= 15:
        rev_score = 5.0
    elif rev <= 30:
        rev_score = 4.0
    elif rev <= 50:
        rev_score = 3.0
    else:
        rev_score = 2.0

    return emp_score + rev_score, None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enrich_company(company_name: str, article_content: str = "") -> dict | None:
    """
    Look up company firmographics via Serper + GPT.
    Falls back to extracting estimates from article content if Serper finds nothing.
    L1: in-memory cache (process lifetime).
    L2: Postgres company_cache table (persists across deploys).
    """
    if not company_name:
        return None

    cache_key = company_name.strip().lower()

    # L1: in-memory
    if cache_key in _memory_cache:
        logger.info(f"Cache hit (memory) for '{company_name}'")
        return _memory_cache[cache_key]

    # L2: database
    try:
        from db import get_cached_company
        cached = get_cached_company(cache_key)
        if cached:
            _memory_cache[cache_key] = cached
            logger.info(f"Cache hit (DB) for '{company_name}'")
            return cached
    except Exception:
        logger.debug("DB cache lookup failed", exc_info=True)

    snippet = _serper_search(company_name)
    if snippet:
        logger.info(f"Serper data for '{company_name}': {snippet[:120]}")
        result = _extract_with_gpt(company_name, snippet)
    elif article_content:
        logger.info(f"No Serper data for '{company_name}' — estimating from article content")
        result = _estimate_from_article(company_name, article_content)
    else:
        logger.info(f"No Serper data for '{company_name}' and no article content — skipping enrichment")
        return None
    if result is None:
        return None

    if not result.get("employee_count"):
        result["employee_count"] = "est. 10-50"
    if not result.get("estimated_revenue"):
        result["estimated_revenue"] = "est. $1M-$5M"

    _memory_cache[cache_key] = result
    try:
        from db import set_cached_company as _set
        _set(cache_key, result)
    except Exception:
        logger.debug("DB cache write failed", exc_info=True)

    logger.info(
        f"Enriched '{company_name}': "
        f"{result.get('hq_city')}, {result.get('hq_state_or_province')}, {result.get('hq_country')} | "
        f"employees={result.get('employee_count')} | rev={result.get('estimated_revenue')}"
    )
    return result


def apply_enrichment(classification: dict, enrichment: dict) -> dict:
    """
    Merge enrichment into classification, run dual-score routing decision.

    Routing requires ALL of:
      - in_tam_geography is True
      - at least one ERP signal
      - not hard-excluded (employees <= 150 AND revenue <= $80M)
      - average of article_score + firmographics_score >= 7.3
    """
    updated = classification.copy()
    updated["enrichment"] = enrichment

    # Location merge — only fill gaps, never override Stage 1 classifier
    hq_state   = enrichment.get("hq_state_or_province")
    hq_country = enrichment.get("hq_country")

    original_location = classification.get("location") or {}
    original_state    = original_location.get("state_or_province")
    original_country  = original_location.get("country")

    if not original_state or not original_country:
        merged_state   = original_state or hq_state
        merged_country = original_country or hq_country
        merged_city    = original_location.get("city") or enrichment.get("hq_city")

        if merged_state or merged_country:
            updated["location"] = {
                "city": merged_city,
                "state_or_province": merged_state,
                "country": merged_country,
            }
            if merged_state and merged_country:
                in_us_tam = merged_country == "US" and merged_state in TAM_US_STATES
                in_ca_tam = merged_country == "Canada" and merged_state in TAM_CA_PROVINCES
                updated["in_tam_geography"] = in_us_tam or in_ca_tam

    rev = enrichment.get("estimated_revenue")
    if rev and updated.get("revenue_estimate") in (None, "unknown", ""):
        updated["revenue_estimate"] = rev

    firmographics_score, exclusion_reason = _firmographics_score(enrichment)

    if exclusion_reason:
        updated["should_route"]        = False
        updated["exclusion_reason"]    = exclusion_reason
        updated["firmographics_score"] = 0.0
        logger.info(f"Hard excluded '{classification.get('company_name')}': {exclusion_reason}")
        return updated

    erp_likelihood      = int(classification.get("erp_likelihood") or 0)
    updated["firmographics_score"] = round(firmographics_score, 1)
    updated["erp_likelihood"]      = erp_likelihood

    geo_ok  = updated.get("in_tam_geography")
    signals = updated.get("erp_signals") or []

    updated["should_route"] = bool(
        geo_ok is True
        and len(signals) > 0
        and erp_likelihood >= _ROUTE_THRESHOLD
        and firmographics_score >= 5.0
    )

    logger.info(
        f"Scored '{classification.get('company_name')}': "
        f"erp_likelihood={erp_likelihood}/10 | firmographics={firmographics_score:.1f} "
        f"| geo={geo_ok} | route={'YES' if updated['should_route'] else 'NO'}"
    )
    return updated
