"""
NLP Analyzer — uses local Gemma via Ollama (OpenAI-compatible API).
"""
import asyncio
import json
import logging
import re
import time
from openai import AsyncOpenAI

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
- priority: Integer from 1 (lowest) to 10 (highest urgency)
- language: One of ["KZ", "ENG", "RU"] — if unclear, default to "RU"
- summary: 1–2 concise sentences in RUSSIAN summarizing the request, shorter than the original.
- next_actions: A short string in RUSSIAN with recommended next actions for the manager (1–3 steps).

Rules for priority:
- Fraudulent Activity → always 9-10
- Application Malfunction with urgent payment → 8-10
- Complaints with strong negative sentiment → 6-8
- Consultations → 1-4
- Spam → 1

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


async def analyze_ticket(description: str, index: int = 0, total: int = 1) -> dict:
    """
    Send a ticket description to Ollama Gemma and return structured NLP analysis.
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
        log.info("[%d/%d] Parsed: type=%s sentiment=%s priority=%s",
                 index, total,
                 result.get("request_type"), result.get("sentiment"), result.get("priority"))

        return {
            "request_type": REQUEST_TYPE_MAP.get(result.get("request_type", ""), "Consultation"),
            "sentiment": SENTIMENT_MAP.get(result.get("sentiment", ""), "Neutral"),
            "priority_score": int(result.get("priority", 5)),
            "language": result.get("language", "RU"),
            "summary": result.get("summary", ""),
            "next_actions": result.get("next_actions", ""),
            "infer_time_ms": infer_time_ms,
        }

    except Exception as e:
        log.error("[%d/%d] Failed after %.1fs: %s", index, total, time.perf_counter() - t_start, e)
        return _fallback()


def update_settings(model_id: str, concurrency: int) -> None:
    """Hot-swap the Ollama model and client concurrency at runtime."""
    global MODEL_ID, CONCURRENCY, _sem
    MODEL_ID = model_id
    CONCURRENCY = concurrency
    _sem = asyncio.Semaphore(CONCURRENCY)
    log.info("NLP settings updated: model=%s concurrency=%d", MODEL_ID, CONCURRENCY)


def _fallback() -> dict:
    return {
        "request_type": "Consultation",
        "sentiment": "Neutral",
        "priority_score": 5,
        "language": "RU",
        "summary": "Не удалось проанализировать — требуется ручная проверка.",
        "next_actions": "Передать на ручную обработку.",
        "infer_time_ms": 0,
    }
