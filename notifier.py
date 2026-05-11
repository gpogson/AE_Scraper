import logging
import os
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

_SIGNAL_COLORS = {
    "leadership change": 0xFEE75C,
    "geographic expansion": 0x57F287,
    "new product launch": 0xEB459E,
    "new funding round": 0x57F287,
    "tech modernization": 0x5865F2,
    "rapid growth": 0x57F287,
    "m&a activity": 0xED4245,
    "supply chain change": 0x99AAB5,
}

_DEFAULT_COLOR = 0x99AAB5


def _embed_color(signals: list[str]) -> int:
    for signal in signals:
        sl = signal.lower()
        for key, color in _SIGNAL_COLORS.items():
            if key in sl:
                return color
    return _DEFAULT_COLOR


def _score_bar(score: float) -> str:
    filled = round(score)
    return "█" * filled + "░" * (10 - filled)


def _location_str(location: dict) -> str:
    parts = [location.get("city"), location.get("state_or_province"), location.get("country")]
    return ", ".join(p for p in parts if p) or "Unknown"


def send_discord_notification(article: dict, classification: dict):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        logger.error("DISCORD_WEBHOOK_URL is not set — skipping notification")
        return

    company             = classification.get("company_name") or "Unknown Company"
    location            = classification.get("location") or {}
    signals             = classification.get("erp_signals") or []
    erp_likelihood      = int(classification.get("erp_likelihood") or 0)
    firmographics_score = float(classification.get("firmographics_score") or 0)
    revenue             = classification.get("revenue_estimate") or "Unknown"
    summary             = classification.get("signal_summary") or ""
    reasoning           = classification.get("likelihood_reasoning") or ""
    sub_industry        = classification.get("sub_industry") or ""

    enrichment      = classification.get("enrichment") or {}
    employees       = enrichment.get("employee_count")
    current_software = enrichment.get("current_software")
    website         = enrichment.get("website")
    enriched        = bool(enrichment)

    company_url    = website or article["url"]
    industry_value = sub_industry or enrichment.get("industry") or "—"

    score_line = (
        f"ERP Likelihood `{erp_likelihood}/10` {_score_bar(erp_likelihood)}  "
        f"Firmographics `{firmographics_score:.1f}` {_score_bar(firmographics_score)}"
    )

    fields = [
        {"name": "\U0001f4f0 Article", "value": f"[Read Article]({article['url']})", "inline": False},
        {"name": "\U0001f4ca Score",   "value": score_line, "inline": False},
        {"name": "\U0001f4cd Location",    "value": _location_str(location) + (" \U0001f50d" if enriched else ""), "inline": True},
        {"name": "\U0001f4b0 Revenue Est.", "value": revenue + (" \U0001f50d" if enriched else ""), "inline": True},
        {"name": "\U0001f465 Employees",   "value": employees + (" \U0001f50d" if enriched else "") if employees else "Unknown", "inline": True},
        {"name": "\U0001f3ed Industry",    "value": industry_value[:512], "inline": True},
    ]

    if current_software:
        fields.append({"name": "\U0001f4bb Current Software", "value": current_software, "inline": True})

    fields.append({
        "name": "⚡ ERP Signals",
        "value": "  |  ".join(f"`{s}`" for s in signals) if signals else "None",
        "inline": False,
    })

    if reasoning:
        fields.append({
            "name": "\U0001f4ca Why this score",
            "value": reasoning[:512],
            "inline": False,
        })

    fields.append({
        "name": "\U0001f4dd Summary",
        "value": summary[:1024] if summary else "—",
        "inline": False,
    })

    embed = {
        "title": f"\U0001f3af {company}",
        "url": company_url,
        "color": _embed_color(signals),
        "fields": fields,
        "footer": {"text": f"Source: {article['source']}  •  {article.get('published', '')}"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        resp = requests.post(webhook_url, json={"username": "ERP Signal Bot", "embeds": [embed]}, timeout=10)
        resp.raise_for_status()
        logger.info(f"Discord notified: {company}")
    except requests.HTTPError as e:
        logger.error(f"Discord HTTP error {e.response.status_code}: {e.response.text}")
    except Exception:
        logger.exception("Discord notification failed")
