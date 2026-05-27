"""
Test any article URL through the full pipeline.

Usage:
    python test_article.py <url>             # classify only
    python test_article.py <url> --notify    # classify + send to Discord

Example:
    python test_article.py https://www.prnewswire.com/news-releases/...
    python test_article.py https://www.prnewswire.com/news-releases/... --notify
"""

import sys
import logging
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")

import requests
from dotenv import load_dotenv

from classifier import classify_article
from enricher import enrich_company, apply_enrichment
from notifier import send_discord_notification

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ERPSignalBot/1.0)"}
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s{2,}")


def _strip_html(text: str) -> str:
    text = _HTML_TAG_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def fetch_article(url: str) -> dict:
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()

    title_match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
    title = _strip_html(title_match.group(1)) if title_match else url
    content = _strip_html(resp.text)[:4000]

    return {
        "id": "test",
        "title": title,
        "url": url,
        "content": content,
        "source": "manual-test",
        "published": "now",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_article.py <url> [--notify]")
        sys.exit(1)

    url = sys.argv[1]
    notify = "--notify" in sys.argv

    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    if notify:
        print("Mode: LIVE (will send to Discord if routed)")
    else:
        print("Mode: DRY RUN (no Discord notification)")
    print('='*60)

    print("\n[1/3] Fetching article...")
    article = fetch_article(url)
    print(f"Title: {article['title'][:80]}")

    print("\n[2/3] Stage 1 — GPT-4o-mini classification...")
    result = classify_article(article)
    if not result:
        print("ERROR: Classification failed")
        sys.exit(1)

    likelihood = result.get("erp_likelihood") or 0
    print(f"Company:        {result.get('company_name')}")
    print(f"Signals:        {result.get('erp_signals')}")
    print(f"ERP Likelihood: {likelihood}/10")
    print(f"Reasoning:      {result.get('likelihood_reasoning')}")
    print(f"Sub-industry:   {result.get('sub_industry')}")

    if likelihood >= 6:
        print("\n[3/3] Stage 2 — Company enrichment (ZoomInfo via Serper.dev)...")
        company_name = result.get("company_name")
        enrichment = enrich_company(company_name)

        if enrichment:
            print(f"HQ:           {enrichment.get('hq_city')}, {enrichment.get('hq_state_or_province')}, {enrichment.get('hq_country')}")
            print(f"Employees:    {enrichment.get('employee_count')}")
            print(f"Revenue:      {enrichment.get('estimated_revenue')}")
            print(f"Website:      {enrichment.get('website')}")
            print(f"Software:     {enrichment.get('current_software')}")
            print(f"Industry:     {enrichment.get('industry')}")

            result = apply_enrichment(result, enrichment)
            print(f"\nFinal route:       {result.get('should_route')}")
            print(f"Final geo:         {result.get('in_tam_geography')}")
            print(f"Firmographics:     {result.get('firmographics_score')}")
            if result.get("exclusion_reason"):
                print(f"Excluded because: {result.get('exclusion_reason')}")
        else:
            print("Enrichment returned no data")
            if likelihood >= 7 and result.get("erp_signals"):
                result["should_route"] = True
                result["unverified_geo"] = True
                result["routing_reason"] = "⚠️ unverified geography/size — ZoomInfo not found"
    else:
        print(f"\n[3/3] Skipping enrichment — erp_likelihood {likelihood}/10 below threshold of 6")

    print(f"\n{'='*60}")
    print(f"FINAL DECISION: {'✅ ROUTE TO DISCORD' if result.get('should_route') else '❌ SKIP'}")
    print(f"Reason: {result.get('routing_reason')}")
    print('='*60)

    if result.get("should_route"):
        if notify:
            print("\nSending to Discord...")
            send_discord_notification(article, result)
            print("Sent!")
        else:
            print("\nRun with --notify to send this to Discord.")
    print()


if __name__ == "__main__":
    main()
