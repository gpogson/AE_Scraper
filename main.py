"""
ERP Signal Agent
================
Polls RSS feeds from PR news wires, classifies each article with GPT-4o-mini
to identify companies in your TAM showing ERP buying signals, and routes
matches to Discord.

Usage:
    python main.py              # Run continuously, polling every 10 minutes
    python main.py --once       # Single run then exit (good for cron jobs)
    python main.py --dry-run    # Classify and log but do NOT send Discord notifications
"""

import argparse
import logging
import sys
import time

import schedule
from dotenv import load_dotenv

from classifier import classify_article
from config import POLL_INTERVAL_MINUTES
from db import init_db, is_seen, mark_seen
from enricher import enrich_company, apply_enrichment
from notifier import send_discord_notification
from scraper import fetch_new_articles

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent.log"),
    ],
)
logger = logging.getLogger(__name__)


def run_pipeline(dry_run: bool = False):
    logger.info("--- Pipeline run starting ---")
    articles = fetch_new_articles()
    logger.info(f"Total articles fetched: {len(articles)}")

    new_count = routed_count = 0

    for article in articles:
        if is_seen(article["id"]):
            continue

        # Mark seen immediately so a crash mid-run doesn't reprocess
        mark_seen(article["id"])
        new_count += 1

        result = classify_article(article)
        if result is None:
            continue

        company_name = result.get("company_name")

        # Only enrich when the article itself is a strong enough signal
        needs_enrichment = (result.get("erp_likelihood") or 0) >= 6

        if needs_enrichment and company_name:
            logger.info(f"Enriching: {company_name}")
            enrichment = enrich_company(company_name)
            if enrichment:
                result = apply_enrichment(result, enrichment)
            else:
                likelihood = result.get("erp_likelihood") or 0
                signals = result.get("erp_signals") or []
                if likelihood >= 7 and signals:
                    result["should_route"] = True
                    result["unverified_geo"] = True
                    result["routing_reason"] = "⚠️ unverified geography/size — ZoomInfo not found"
                    logger.info(f"Fallback route (no ZoomInfo): {company_name} | likelihood={likelihood}/10")

        if result.get("should_route"):
            routed_count += 1
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would notify: {result.get('company_name')} "
                    f"| signals={result.get('erp_signals')} "
                    f"| erp_likelihood={result.get('erp_likelihood')}"
                )
            else:
                send_discord_notification(article, result)

    logger.info(
        f"--- Pipeline done: {new_count} new articles processed, "
        f"{routed_count} routed to Discord ---"
    )


def main():
    parser = argparse.ArgumentParser(description="ERP Signal Agent")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run pipeline once and exit instead of looping",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify articles but skip Discord notifications",
    )
    args = parser.parse_args()

    init_db()

    if args.once:
        run_pipeline(dry_run=args.dry_run)
        return

    logger.info(
        f"Starting ERP Signal Agent — polling every {POLL_INTERVAL_MINUTES} minutes"
    )

    # Run once immediately, then on schedule
    run_pipeline(dry_run=args.dry_run)
    schedule.every(POLL_INTERVAL_MINUTES).minutes.do(
        run_pipeline, dry_run=args.dry_run
    )

    while True:
        schedule.run_pending()
        time.sleep(15)


if __name__ == "__main__":
    main()
