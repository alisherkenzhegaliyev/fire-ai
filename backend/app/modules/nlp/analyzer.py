"""
NLP Analyzer — uses local Gemma via Ollama (OpenAI-compatible API).
"""
import asyncio
import json
import logging
import re
import time
from openai import AsyncOpenAI

from app.modules.nlp.priority import score_priority

logging.basicConfig(level=logging.INFO, format="%(asctime)s [NLP] %(message)s")
log = logging.getLogger(__name__)

# ── Model Configuration ──────────────────────────────────────────────────────
MODEL_ID = "gemma3:4b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
CONCURRENCY = 6   # keep Ollama's queue full (match OLLAMA_NUM_PARALLEL + buffer)
NUM_CTX = 1024    # context window per request — system prompt+ticket+reply fits ~700 tokens

client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
_sem = asyncio.Semaphore(CONCURRENCY)

# ── Russian → English mappings ────────────────────────────────────────────────
REQUEST_TYPE_MAP: dict[str, str] = {
    "Жалоба": "Complaint",
    "Смена данных": "DataChange",
    "Консультация": "Consultation",
    "Претензия": "Claim",
    "Неработоспособность приложения": "AppMalfunction",
    "Мошеннические действия": "FraudulentActivity",
    "Спам": "Spam",
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

SYSTEM_PROMPT = """You are an AI assistant for a bank's customer support routing system.
Analyze the given customer request and return a JSON object with the following fields:

- request_type: One of ["Жалоба", "Смена данных", "Консультация", "Претензия", "Неработоспособность приложения", "Мошеннические действия", "Спам"]
- sentiment: One of ["Положительная", "Нейтральная", "Негативная"]
- language: One of ["KZ", "ENG", "RU"] — if unclear, default to "RU"
- summary: 1–2 concise sentences in RUSSIAN summarizing the request, shorter than the original.
- next_actions: A short string in RUSSIAN with recommended next actions for the manager (1–3 steps).

Return ONLY valid JSON. All text values must be written in Russian."""


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return m.group(0).strip() if m else text


async def analyze_ticket(description: str, segment: str = "Mass", index: int = 0, total: int = 1) -> dict:
    """
    Send a ticket description to Ollama Gemma and return structured NLP analysis.
    Priority is computed deterministically from request_type + sentiment + segment
    using score_priority() instead of relying on the LLM.
    """
    t_start = time.perf_counter()
    log.info("[%d/%d] Analyzing ticket (len=%d chars) …", index, total, len(description))

    try:
        async with _sem:
            t_infer_start = time.perf_counter()
            response = await client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": description},
                ],
                max_tokens=200,
                temperature=0,
                extra_body={"options": {"num_ctx": NUM_CTX}},
            )
            infer_time_ms = round((time.perf_counter() - t_infer_start) * 1000)

        t_infer = time.perf_counter() - t_start
        content = response.choices[0].message.content or ""
        log.info("[%d/%d] Inference done in %.1fs, raw output length=%d", index, total, t_infer, len(content))

        result = json.loads(_extract_json(content))
        raw_request_type = result.get("request_type", "Консультация")
        raw_sentiment = result.get("sentiment", "Нейтральная")

        priority = score_priority(raw_request_type, raw_sentiment, segment)
        log.info("[%d/%d] Parsed: type=%s sentiment=%s priority=%d (scored)",
                 index, total, raw_request_type, raw_sentiment, priority)

        return {
            "request_type": REQUEST_TYPE_MAP.get(raw_request_type, "Consultation"),
            "sentiment": SENTIMENT_MAP.get(raw_sentiment, "Neutral"),
            "priority_score": priority,
            "language": result.get("language", "RU"),
            "summary": result.get("summary", ""),
            "next_actions": result.get("next_actions", ""),
            "infer_time_ms": infer_time_ms,
        }

    except Exception as e:
        log.error("[%d/%d] Failed after %.1fs: %s", index, total, time.perf_counter() - t_start, e)
        return _fallback(segment)


def update_settings(model_id: str, concurrency: int) -> None:
    """Hot-swap the Ollama model and client concurrency at runtime."""
    global MODEL_ID, CONCURRENCY, _sem
    MODEL_ID = model_id
    CONCURRENCY = concurrency
    _sem = asyncio.Semaphore(CONCURRENCY)
    log.info("NLP settings updated: model=%s concurrency=%d", MODEL_ID, CONCURRENCY)


def _fallback(segment: str = "Mass") -> dict:
    return {
        "request_type": "Consultation",
        "sentiment": "Neutral",
        "priority_score": score_priority("Консультация", "Нейтральная", segment),
        "language": "RU",
        "summary": "Не удалось проанализировать — требуется ручная проверка.",
        "next_actions": "Передать на ручную обработку.",
        "infer_time_ms": 0,
    }
