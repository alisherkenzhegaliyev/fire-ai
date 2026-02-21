"""
NLP Analyzer — uses OpenRouter (openai/gpt-oss-120b:free) to classify and summarize tickets.
"""
import json
import re
from openai import OpenAI
from app.core.config import settings

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)
MODEL = "openai/gpt-oss-120b:free"

# ── Russian → English mappings ────────────────────────────────────────────────
REQUEST_TYPE_MAP: dict[str, str] = {
    "Жалоба": "Complaint",
    "Смена данных": "DataChange",
    "Консультация": "Consultation",
    "Претензия": "Claim",
    "Неработоспособность приложения": "AppMalfunction",
    "Мошеннические действия": "FraudulentActivity",
    "Спам": "Spam",
    # passthrough if model already returns English
    "Complaint": "Complaint",
    "DataChange": "DataChange",
    "Consultation": "Consultation",
    "Claim": "Claim",
    "AppMalfunction": "AppMalfunction",
    "FraudulentActivity": "FraudulentActivity",
    "Spam": "Spam",
}

SENTIMENT_MAP: dict[str, str] = {
    "Положительная": "Positive",
    "Нейтральная": "Neutral",
    "Негативная": "Negative",
    "Positive": "Positive",
    "Neutral": "Neutral",
    "Negative": "Negative",
}

SYSTEM_PROMPT = """
You are an AI assistant for a bank's customer support routing system.
Analyze the given customer request and return a JSON object with the following fields:

- request_type: One of ["Жалоба", "Смена данных", "Консультация", "Претензия", "Неработоспособность приложения", "Мошеннические действия", "Спам"]
- sentiment: One of ["Положительная", "Нейтральная", "Негативная"]
- priority: Integer from 1 (lowest) to 10 (highest urgency)
- language: One of ["KZ", "ENG", "RU"] — if unclear, default to "RU"
- summary: Must contain 1–2 concise sentences summarizing the request and must be shorter than the original customer description.
- next_actions: A short string with recommended next actions for the manager (1–3 steps)

Rules for priority:
- Fraudulent Activity → always 9-10
- Application Malfunction with urgent payment → 8-10
- Complaints with strong negative sentiment → 6-8
- Consultations → 1-4
- Spam → 1

Return ONLY valid JSON. No markdown, no explanation.
"""


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return m.group(0).strip() if m else text


def analyze_ticket(description: str) -> dict:
    """
    Send a ticket description to OpenRouter and return structured NLP analysis.
    Returns English-mapped values compatible with the frontend types.
    """
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": description},
            ],
            temperature=0,
            extra_body={"reasoning": {"enabled": True}},
        )
        content = response.choices[0].message.content or ""
        result = json.loads(_extract_json(content))

        return {
            "request_type": REQUEST_TYPE_MAP.get(result.get("request_type", ""), "Consultation"),
            "sentiment": SENTIMENT_MAP.get(result.get("sentiment", ""), "Neutral"),
            "priority_score": int(result.get("priority", 5)),
            "language": result.get("language", "RU"),
            "summary": result.get("summary", ""),
            "next_actions": result.get("next_actions", ""),
        }

    except json.JSONDecodeError:
        return _fallback()
    except Exception:
        return _fallback()


def _fallback() -> dict:
    return {
        "request_type": "Consultation",
        "sentiment": "Neutral",
        "priority_score": 5,
        "language": "RU",
        "summary": "Could not analyze — please review manually.",
        "next_actions": "Manual review required.",
    }