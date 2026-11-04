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
    "new sales channel": 0xEB459E,
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


def _safe_url(url) -> str | None:
    """Discord rejects the whole embed if a URL lacks an http(s) scheme or has spaces."""
    url = str(url or "").strip()
    if not url or url.lower() in ("null", "none", "unknown", "n/a") or " " in url:
        return None
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url.lstrip("/")
    return url


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

    enrichment       = classification.get("enrichment") or {}
    employees        = enrichment.get("employee_count")
    current_software = enrichment.get("current_software")
    website          = enrichment.get("website")
    enriched         = bool(enrichment)

    article_url    = _safe_url(article.get("url"))
    company_url    = _safe_url(website) or article_url
    industry_value = sub_industry or enrichment.get("industry") or "—"

    score_line = (
        f"ERP Likelihood `{erp_likelihood}/10` {_score_bar(erp_likelihood)}  "
        f"Firmographics `{firmographics_score:.1f}` {_score_bar(firmographics_score)}"
    )

    trigger_event = classification.get("trigger_event")
    stage         = (classification.get("signal_stage") or "").lower()

    fields = []
    if trigger_event:
        stage_tag = "\U0001f5d3️ PLANNED" if stage == "planned" else "✅ COMPLETED" if stage == "completed" else ""
        fields.append({"name": "\U0001f514 Trigger", "value": f"{trigger_event}  {stage_tag}".strip(), "inline": False})

    fields += [
        {"name": "\U0001f4f0 Article", "value": f"[Read Article]({article_url})" if article_url else "—", "inline": False},
        {"name": "\U0001f4ca Score",   "value": score_line, "inline": False},
        {"name": "\U0001f4cd Location",     "value": _location_str(location) + (" \U0001f50d" if enriched else ""), "inline": True},
        {"name": "\U0001f4b0 Revenue Est.", "value": revenue + (" \U0001f50d" if enriched else ""), "inline": True},
        {"name": "\U0001f465 Employees",    "value": (employees + (" \U0001f50d" if enriched else "") if employees else "Unknown"), "inline": True},
        {"name": "\U0001f3ed Industry",     "value": industry_value[:512], "inline": True},
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

    # Discord rejects empty or over-length field values (1024 chars max)
    for field in fields:
        field["value"] = (str(field["value"]).strip() or "—")[:1024]

    embed = {
        "title": f"\U0001f3af {company}"[:256],
        "color": _embed_color(signals),
        "fields": fields,
        "footer": {"text": f"Source: {article['source']}  •  {article.get('published', '')}"[:2048]},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if company_url:
        embed["url"] = company_url

    try:
        resp = requests.post(webhook_url, json={"username": "ERP Signal Bot", "embeds": [embed]}, timeout=10)
        resp.raise_for_status()
        logger.info(f"Discord notified: {company}")
    except requests.HTTPError as e:
        logger.error(
            f"Discord HTTP error {e.response.status_code}: {e.response.text} "
            f"| company={company!r} url={company_url!r}"
        )
    except Exception:
        logger.exception("Discord notification failed")
