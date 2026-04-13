import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import quote

import requests

from config import TAM_US_STATES, TAM_CA_PROVINCES

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ERPSignalBot/1.0)"}

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
# Free data sources
# ---------------------------------------------------------------------------

def _duckduckgo_instant(company_name: str) -> dict:
    """DuckDuckGo Instant Answer API — free, no key needed."""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": company_name,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1",
            },
            headers=_HEADERS,
            timeout=10,
        )
        data = resp.json()
        return {
            "abstract": data.get("Abstract", ""),
            "website": data.get("AbstractURL", ""),
            "type": data.get("Type", ""),
            "infobox": str(data.get("Infobox", "")),
        }
    except Exception:
        logger.debug(f"DuckDuckGo lookup failed for: {company_name}")
        return {}


def _wikipedia_summary(company_name: str) -> str:
    """Wikipedia REST API summary — free, often has HQ, employees, revenue."""
    try:
        slug = company_name.replace(" ", "_")
        resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(slug)}",
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("extract", "")
    except Exception:
        pass
    return ""


def _fetch_website_text(url: str) -> str:
    """Fetch a company's website and return plain text (first 2000 chars)."""
    if not url:
        return ""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        if resp.status_code == 200:
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s{2,}", " ", text)
            return text[:2000]
    except Exception:
        pass
    return ""


def _duckduckgo_search(company_name: str) -> str:
    """DuckDuckGo HTML search for company size/revenue snippets."""
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": f'"{company_name}" employees OR revenue OR headquarters OR "founded in"'},
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            timeout=10,
        )
        # Extract result snippets
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
        clean = [re.sub(r"<[^>]+>", " ", s).strip() for s in snippets[:5]]
        return " | ".join(clean)
    except Exception:
        pass
    return ""


def _find_website(company_name: str) -> str:
    """Google 'I'm Feeling Lucky' — returns the top result URL for the company name."""
    from urllib.parse import urlparse, parse_qs
    try:
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": company_name, "btnI": "1"},
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            timeout=10,
            allow_redirects=True,
        )
        # Google lands on /url?q=<target> after the redirect
        qs = parse_qs(urlparse(resp.url).query)
        url = qs.get("q", [""])[0]
        if not url:
            url = resp.url
        skip = ("google.", "bing.", "yahoo.", "duckduckgo.", "facebook.", "twitter.",
                "linkedin.", "youtube.", "wikipedia.", "globenewswire.", "prnewswire.",
                "businesswire.", "sec.gov", "bloomberg.", "reuters.", "crunchbase.")
        if url and not any(s in url for s in skip):
            return url.split("?")[0].rstrip("/")
    except Exception:
        pass
    return ""


def _fetch_about_page(website_url: str) -> str:
    """Try fetching /about or /about-us page for headcount and office info."""
    if not website_url:
        return ""
    base = website_url.rstrip("/")
    for path in ["/about", "/about-us", "/company", "/team"]:
        try:
            resp = requests.get(base + path, headers=_HEADERS, timeout=8)
            if resp.status_code == 200:
                text = re.sub(r"<[^>]+>", " ", resp.text)
                text = re.sub(r"\s{2,}", " ", text)
                return text[:1500]
        except Exception:
            continue
    return ""


def _google_news_company(company_name: str) -> str:
    """Google News RSS search for recent company news — reveals growth trajectory."""
    try:
        from urllib.parse import quote as _quote
        url = f"https://news.google.com/rss/search?q={_quote(company_name)}&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        import feedparser
        feed = feedparser.parse(resp.content)
        titles = [e.get("title", "") for e in feed.entries[:5]]
        return " | ".join(titles)
    except Exception:
        pass
    return ""


def _opencorporates(company_name: str) -> str:
    """OpenCorporates free API — returns incorporation state and company status."""
    try:
        resp = requests.get(
            "https://api.opencorporates.com/v0.4/companies/search",
            params={"q": company_name, "jurisdiction_code": "us", "per_page": 3},
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            companies = resp.json().get("results", {}).get("companies", [])
            if companies:
                c = companies[0]["company"]
                return (
                    f"Incorporated: {c.get('jurisdiction_code', '?').upper()} | "
                    f"Status: {c.get('current_status', '?')} | "
                    f"Registered: {c.get('incorporation_date', '?')}"
                )
    except Exception:
        pass
    return ""


def _find_linkedin_url(company_name: str) -> str:
    """Search DuckDuckGo HTML for a LinkedIn company URL."""
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": f"{company_name} site:linkedin.com/company"},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=10,
        )
        urls = re.findall(r'https://[a-z]+\.linkedin\.com/company/[^\s"&]+', resp.text)
        if urls:
            # Clean and return first match
            url = urls[0].split("?")[0].rstrip("/")
            return url
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# GPT synthesis
# ---------------------------------------------------------------------------

_SYNTHESIS_PROMPT = """You are a company research analyst. Using the search data below, extract structured firmographic information about "{company_name}".

RULES:
- employee_count: ALWAYS provide a number or range. NEVER null. If not stated, estimate from \
  any available signals — industry, revenue, company stage, language like "regional", "startup", \
  "family-owned". Examples: "12", "25-50", "~40", "est. 10-30".
- estimated_revenue: ALWAYS provide an estimate. NEVER null. Reason from headcount, funding \
  amounts, industry norms, or company stage. Use these as guides: \
  1-10 employees ≈ under $1M, 10-50 ≈ $1M-$5M, 50-100 ≈ $5M-$15M, 100+ ≈ over $15M. \
  Examples: "$3M", "$5M-$10M", "est. $2M".
- hq_state_or_province: 2-letter US state (WA, OR, CA …) or Canadian province (BC, AB …), \
  or null only if genuinely undetectable.
- hq_country: "US", "Canada", or "other". null only if genuinely undetectable.
- current_software: any ERP, accounting, or ops software explicitly mentioned (QuickBooks, \
  SAP, NetSuite, Sage, etc.), or null.

--- DuckDuckGo Instant Answer ---
{ddg_abstract}
{ddg_website}
{ddg_infobox}

--- DuckDuckGo Search Snippets ---
{ddg_search}

--- Wikipedia ---
{wikipedia}

--- Company Website Homepage ---
{website_text}

--- Company About/Team Page ---
{about_text}

--- Recent News Headlines ---
{news_headlines}

--- OpenCorporates Registry ---
{opencorporates}

Reply ONLY with this exact JSON (no markdown, no explanation):
{{
  "hq_city": "city or null",
  "hq_state_or_province": "2-letter code or null",
  "hq_country": "US or Canada or other or null",
  "employee_count": "always a number or range e.g. '25', '50-100', '~40'",
  "employee_count_est": <integer — single best-estimate headcount, use midpoint of any range>,
  "estimated_revenue": "always an estimate e.g. '$3M', '$5M-$10M'",
  "revenue_millions_est": <float — single best-estimate revenue in millions USD, e.g. 7.5 for "$5M-$10M">,
  "website": "official website URL or null",
  "industry": "one-line description or null",
  "current_software": "known ERP/accounting software or null",
  "notes": "anything relevant about size or growth stage"
}}"""


def _synthesize_with_gpt(
    company_name: str,
    ddg: dict,
    ddg_search: str,
    wikipedia: str,
    website_text: str,
    about_text: str,
    news_headlines: str,
    opencorporates: str,
) -> dict | None:
    """Feed raw search data to GPT-4o-mini to extract structured company info."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        prompt = _SYNTHESIS_PROMPT.format(
            company_name=company_name,
            ddg_abstract=ddg.get("abstract", ""),
            ddg_website=ddg.get("website", ""),
            ddg_infobox=ddg.get("infobox", ""),
            ddg_search=ddg_search[:500] if ddg_search else "",
            wikipedia=wikipedia[:1000] if wikipedia else "",
            website_text=website_text[:800] if website_text else "",
            about_text=about_text[:800] if about_text else "",
            news_headlines=news_headlines[:300] if news_headlines else "",
            opencorporates=opencorporates or "",
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=300,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        logger.exception(f"GPT synthesis failed for: {company_name}")
        return None


# ---------------------------------------------------------------------------
# Firmographics scoring
# ---------------------------------------------------------------------------

_ROUTE_THRESHOLD = 7.3
_MAX_EMPLOYEES   = 150
_MAX_REVENUE_M   = 80.0


def _firmographics_score(enrichment: dict) -> tuple[float, str | None]:
    """
    Score 0.0–10.0 based on how well the company fits the target profile.
    Returns (score, exclusion_reason). exclusion_reason is set (and score=0)
    when the company exceeds hard limits — skip it entirely regardless of article score.

    Scoring breakdown (max 10 pts):
      Employee component (0–5 pts):
        10–50   → 5.0   sweet spot
        51–100  → 4.5
        101–150 → 3.5
        <10     → 3.0   possibly too small
        unknown → 3.5   take a risk
        >150    → EXCLUDED

      Revenue component (0–5 pts):
        $1M–$15M  → 5.0  sweet spot
        $15M–$30M → 4.0
        $30M–$50M → 3.0
        $50M–$80M → 2.0
        <$1M      → 2.5  possibly too small
        unknown   → 3.5  take a risk
        >$80M     → EXCLUDED
    """
    emp = enrichment.get("employee_count_est")
    rev = enrichment.get("revenue_millions_est")

    # Hard exclusions
    if emp is not None and emp > _MAX_EMPLOYEES:
        return 0.0, f"employee count too high (~{emp})"
    if rev is not None and rev > _MAX_REVENUE_M:
        return 0.0, f"revenue too high (~${rev:.0f}M)"

    # Employee component
    if emp is None:
        emp_score = 3.5
    elif emp <= 9:
        emp_score = 3.0
    elif emp <= 50:
        emp_score = 5.0
    elif emp <= 100:
        emp_score = 4.5
    else:  # 101–150
        emp_score = 3.5

    # Revenue component
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
    else:  # 50–80
        rev_score = 2.0

    return emp_score + rev_score, None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enrich_company(company_name: str) -> dict | None:
    """
    Look up a company using free sources (DuckDuckGo + Wikipedia),
    synthesize with GPT-4o-mini, and find their LinkedIn URL.
    Results are cached to company_cache.json so each company is only looked up once.
    """
    if not company_name:
        return None

    cache_key = company_name.strip().lower()
    if cache_key in _company_cache:
        logger.info(f"Cache hit for '{company_name}'")
        return _company_cache[cache_key]

    ddg = _duckduckgo_instant(company_name)
    website_url = ddg.get("website", "") or _find_website(company_name)

    # Run all free lookups
    ddg_search = _duckduckgo_search(company_name)
    wikipedia = _wikipedia_summary(company_name)
    website_text = _fetch_website_text(website_url)
    about_text = _fetch_about_page(website_url)
    news_headlines = _google_news_company(company_name)
    opencorporates = _opencorporates(company_name)
    linkedin = _find_linkedin_url(company_name)

    result = _synthesize_with_gpt(
        company_name, ddg, ddg_search, wikipedia,
        website_text, about_text, news_headlines, opencorporates,
    )
    if result is None:
        return None

    # Code-level fallbacks — GPT should never return these but guard anyway
    if not result.get("employee_count"):
        result["employee_count"] = "est. 10-50"
    if not result.get("estimated_revenue"):
        result["estimated_revenue"] = "est. $1M-$5M"

    result["linkedin_url"] = linkedin or None
    if not result.get("website") and website_url:
        result["website"] = website_url

    _company_cache[cache_key] = result
    _save_cache(_company_cache)

    logger.info(
        f"Enriched '{company_name}': "
        f"{result.get('hq_city')}, {result.get('hq_state_or_province')}, {result.get('hq_country')} | "
        f"employees={result.get('employee_count')} | "
        f"rev={result.get('estimated_revenue')} | "
        f"linkedin={'yes' if linkedin else 'no'}"
    )
    return result


def apply_enrichment(classification: dict, enrichment: dict) -> dict:
    """
    Merge enrichment data into classification, score both article fit and
    firmographics, and make a final routing decision.

    Routing requires ALL of:
      - in_tam_geography is True
      - at least one ERP signal
      - not hard-excluded (employees <= 150 AND revenue <= $80M)
      - average of article_score + firmographics_score >= 7.3
    """
    updated = classification.copy()
    updated["enrichment"] = enrichment

    # --- Location merge (only fill gaps, never override Stage 1) -----------
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

    # --- Hard exclusion + firmographics score ------------------------------
    firmographics_score, exclusion_reason = _firmographics_score(enrichment)

    if exclusion_reason:
        updated["should_route"]       = False
        updated["exclusion_reason"]   = exclusion_reason
        updated["firmographics_score"] = 0.0
        logger.info(f"Hard excluded '{classification.get('company_name')}': {exclusion_reason}")
        return updated

    # --- Dual score average -----------------------------------------------
    article_score = float(classification.get("article_score") or 5.0)
    avg_score     = (article_score + firmographics_score) / 2

    updated["article_score"]       = round(article_score, 1)
    updated["firmographics_score"] = round(firmographics_score, 1)
    updated["avg_score"]           = round(avg_score, 1)

    geo_ok  = updated.get("in_tam_geography")
    signals = updated.get("erp_signals") or []

    updated["should_route"] = bool(
        geo_ok is True
        and len(signals) > 0
        and avg_score >= _ROUTE_THRESHOLD
    )

    logger.info(
        f"Scored '{classification.get('company_name')}': "
        f"article={article_score:.1f} | firmographics={firmographics_score:.1f} "
        f"| avg={avg_score:.1f} | route={'YES' if updated['should_route'] else 'NO'}"
    )
    return updated
