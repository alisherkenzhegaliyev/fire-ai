"""
AI Agent Visualizer — uses OpenRouter (openai/gpt-oss-120b:free) to answer natural language
questions about the in-memory ticket dataset and generate chart payloads.
"""
import json
import re
from collections import Counter
from openai import OpenAI

from app.core.config import settings

_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=settings.hf_token,
)
MODEL = "openai/gpt-oss-120b"


# ── Data summarisation helpers ────────────────────────────────────────────────

def _count(tickets: list[dict], field: str) -> dict[str, int]:
    return dict(Counter(t.get(field, "") for t in tickets if t.get(field)))


def _build_context(tickets: list[dict], managers: list[dict]) -> str:
    """Compact JSON summary of the session data sent as LLM context."""
    return json.dumps({
        "total_tickets": len(tickets),
        "by_segment": _count(tickets, "segment"),
        "by_request_type": _count(tickets, "request_type"),
        "by_sentiment": _count(tickets, "sentiment"),
        "by_language": _count(tickets, "language"),
        "by_city": _count(tickets, "city"),
        "by_country": _count(tickets, "country"),
        "avg_priority": round(
            sum(t.get("priority_score", 5) for t in tickets) / max(len(tickets), 1), 1
        ),
        "managers": [
            {
                "name": m.get("full_name"),
                "workload": m.get("workload", 0),
                "office": m.get("business_unit"),
            }
            for m in managers[:20]
        ],
        "ticket_sample": [
            {
                "segment": t.get("segment"),
                "request_type": t.get("request_type"),
                "sentiment": t.get("sentiment"),
                "language": t.get("language"),
                "city": t.get("city"),
                "priority_score": t.get("priority_score"),
            }
            for t in tickets[:10]
        ],
    }, ensure_ascii=False)


AGENT_SYSTEM_PROMPT = """
You are a data analyst AI assistant for a bank's customer support ticket routing dashboard.
You will be given a JSON summary of the uploaded ticket dataset and a user question.

Your job is to:
1. Answer the question accurately based on the provided data.
2. If a chart would help, include chart data.

Return ONLY a single valid JSON object with these fields:
{
  "answer": "A concise, helpful natural language answer (2-4 sentences)",
  "chart_type": "bar" | "pie" | "line" | "scatter" | null,
  "chart_title": "Descriptive chart title" | null,
  "chart_data": [{"label": "...", "value": <number>}, ...] | null,
  "x_key": "label" | null,
  "y_key": "value" | null
}

Rules:
- Use "pie" for distribution/proportion questions (segment breakdown, sentiment split, etc.)
- Use "bar" for comparisons across categories (by city, by type, etc.)
- If no chart is needed, set chart_type, chart_title, chart_data, x_key, y_key to null.
- chart_data items MUST always have "label" (string) and "value" (number) keys.
- Return ONLY valid JSON. No markdown, no explanation outside the JSON.
"""


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return m.group(0).strip() if m else text


# ── Public handler ────────────────────────────────────────────────────────────

def handle_query(question: str, tickets: list[dict], managers: list[dict]) -> dict:
    """
    Answer a natural language question about the session's ticket data.
    Returns a dict compatible with AgentQueryResponse:
      { answer, chart_data: { type, title, data, x_key, y_key } | None }
    """
    context = _build_context(tickets, managers)

    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Dataset summary:\n{context}\n\nUser question: {question}"},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        result = json.loads(_extract_json(content))
    except Exception:
        return {
            "answer": "Sorry, I could not process your question right now.",
            "chart_data": None,
        }

    chart_data = None
    if result.get("chart_type") and result.get("chart_data"):
        chart_data = {
            "type": result["chart_type"],
            "title": result.get("chart_title", ""),
            "data": result["chart_data"],
            "x_key": result.get("x_key", "label"),
            "y_key": result.get("y_key", "value"),
        }

    return {
        "answer": result.get("answer", "No answer returned."),
        "chart_data": chart_data,
    }