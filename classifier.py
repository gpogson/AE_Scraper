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
    Send the article to GPT-4o-mini for ERP signal classification.
    Returns parsed JSON dict, or None on failure.
    Geography and size checks happen downstream in enrichment.
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
            max_tokens=600,
        )

        raw = response.choices[0].message.content
        result = json.loads(raw)

        likelihood = result.get("erp_likelihood", 0)
        company = result.get("company_name", "?")
        signals = result.get("erp_signals", [])
        reasoning = result.get("likelihood_reasoning", "")

        logger.info(
            f"Classified '{article['title'][:55]}...' "
            f"→ {company} | likelihood={likelihood}/10 | signals={signals} | {reasoning[:80]}"
        )

        return result

    except json.JSONDecodeError:
        logger.error(f"Bad JSON from classifier for: {article['title'][:60]}")
        return None
    except Exception:
        logger.exception(f"Classifier error for: {article['title'][:60]}")
        return None
