import json
import logging
import os

from openai import OpenAI

from config import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_PROMPT

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def classify_article(article: dict) -> dict | None:
    """
    Send the article to GPT-4o-mini for TAM + ERP signal classification.
    Returns parsed JSON dict, or None on failure.
    """
    prompt = CLASSIFICATION_USER_PROMPT.format(
        title=article["title"],
        source=article["source"],
        content=article["content"],
    )

    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=500,
        )

        raw = response.choices[0].message.content
        result = json.loads(raw)

        should = result.get("should_route", False)
        article_score = result.get("article_score", 0)
        company = result.get("company_name", "?")

        if should:
            reason = result.get("routing_reason", "")
            logger.info(
                f"Classified '{article['title'][:55]}...' "
                f"→ ROUTE ✓ | {company} | article_score={article_score:.1f}/10 | {reason}"
            )
        else:
            geo = result.get("in_tam_geography")
            rev = result.get("revenue_in_range")
            signals = result.get("erp_signals", [])
            skip_reasons = []
            if geo is False:
                loc = result.get("location", {})
                location_str = ", ".join(filter(None, [loc.get("state_or_province"), loc.get("country")]))
                skip_reasons.append(f"outside TAM geography ({location_str or 'unknown location'})")
            if rev is False:
                skip_reasons.append(f"revenue out of range ({result.get('revenue_estimate', '?')})")
            if not signals:
                skip_reasons.append("no ERP signals")
            skip_str = " | ".join(skip_reasons) if skip_reasons else result.get("routing_reason", "no reason given")
            logger.info(
                f"Classified '{article['title'][:55]}...' "
                f"→ skip | {company} | score={article_score:.1f}/10 | {skip_str}"
            )
        return result

    except json.JSONDecodeError:
        logger.error(f"Bad JSON from classifier for: {article['title'][:60]}")
        return None
    except Exception:
        logger.exception(f"Classifier error for: {article['title'][:60]}")
        return None
