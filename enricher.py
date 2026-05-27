import json
import logging
import os
from pathlib import Path

import requests

from config import TAM_US_STATES, TAM_CA_PROVINCES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Company cache — persists across runs so each company is only looked up once
# ---------------------------------------------------------------------------

_COMPANY_CACHE_FILE = Path(__file__).parent / "company_cache.json"


def _load_cache() -> dict:
    if _COMPANY_CACHE_FILE.exists():
        try:
            return json.loads(_COMPANY_CACHE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: dict) -> None:
    _COMPANY_CACHE_FILE.write_text(json.dumps(cache, indent=2))


_company_cache: dict = _load_cache()


# ---------------------------------------------------------------------------
# Serper.dev Search — ZoomInfo snippet
# ---------------------------------------------------------------------------

def _zoominfo_data(company_name: str) -> str:
    """
    Search Serper.dev (Google) for the company's ZoomInfo page.
    Returns a combined text block from the organic snippet + People Also Ask Q&A.
    """
    api_key = os.environ.get("SERPER_API_KEY", "")
    if not api_key:
        logger.warning("SERPER_API_KEY not set — skipping enrichment")
        return ""

    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            json={"q": f'"{company_name}" site:zoominfo.com/c/', "num": 5},
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

        # Organic result snippet (employee count, HQ, industry summary)
        for r in data.get("organic", []):
            if "zoominfo.com" in r.get("link", ""):
                snippet = r.get("snippet", "")
                if snippet:
                    parts.append(snippet)
                break

        # People Also Ask — structured Q&A sourced from ZoomInfo
        # Keep company-level facts only; skip individual employee entries
        keep = {"revenue", "employee", "headquarter", "address", "location",
                "industry", "founded", "size", "website"}
        skip = {"email", "phone", "work in", "work for", "contact", "role in",
                "latest job", "direct phone", "colleague", "based", "education",
                "stock symbol", "naics", "sic code", "competition", "social media",
                "acquired", "technology"}
        import re
        strip_tags = re.compile(r"<[^>]+>")
        for faq in data.get("peopleAlsoAsk", []):
            q = faq.get("question", "").lower()
            if any(s in q for s in skip):
                continue
            if any(k in q for k in keep):
                a = strip_tags.sub("", faq.get("snippet", "")).strip()
                if a:
                    parts.append(f"{faq['question']}: {a}")

        return "\n".join(parts)

    except Exception:
        logger.debug(f"Serper ZoomInfo search failed for: {company_name}")
    return ""


# ---------------------------------------------------------------------------
# GPT extraction
# ---------------------------------------------------------------------------

_EXTRACT_PROMPT = """Extract firmographic data from this ZoomInfo snippet about "{company_name}".

Snippet: {snippet}

Rules:
- employee_count: exact string from snippet e.g. "42", "50-200". If missing, estimate from revenue or industry.
- employee_count_est: integer best-estimate (midpoint if range)
- estimated_revenue: exact string from snippet e.g. "$8M". If missing, estimate from headcount.
- revenue_millions_est: float best-estimate in millions e.g. 8.0
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
  "industry": "string or null"
}}"""


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

def enrich_company(company_name: str) -> dict | None:
    """
    Pull a ZoomInfo snippet via Brave Search, extract firmographics with GPT.
    Results are cached to company_cache.json so each company is only looked up once.
    """
    if not company_name:
        return None

    cache_key = company_name.strip().lower()
    if cache_key in _company_cache:
        logger.info(f"Cache hit for '{company_name}'")
        return _company_cache[cache_key]

    snippet = _zoominfo_data(company_name)
    if not snippet:
        logger.info(f"No ZoomInfo data found for '{company_name}' — skipping enrichment")
        return None

    logger.info(f"ZoomInfo data for '{company_name}': {snippet[:120]}")

    result = _extract_with_gpt(company_name, snippet)
    if result is None:
        return None

    if not result.get("employee_count"):
        result["employee_count"] = "est. 10-50"
    if not result.get("estimated_revenue"):
        result["estimated_revenue"] = "est. $1M-$5M"

    _company_cache[cache_key] = result
    _save_cache(_company_cache)

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
