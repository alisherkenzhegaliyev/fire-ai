"""
LangGraph ReAct agent — answers natural language questions about the ticket dataset.

Two entry points:
  - run_agent()    → blocking, returns full result dict (kept for backward compat)
  - stream_agent() → generator that yields SSE-ready event dicts as the agent reasons
"""
import json
import re
from typing import Generator

from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.mcp_server import get_ticket_stats, get_tickets, filter_tickets, get_priority_breakdown

SYSTEM_PROMPT = """\
You are a data analyst AI assistant for a bank's customer support routing dashboard.
You have access to tools that query a PostgreSQL database of enriched support tickets.

## Response format rules
- Always call tools to get real data before answering — never guess counts or values.
- Format ALL responses using Markdown: use ## headings, - bullet lists, and **bold** for key numbers.
- Structure responses with a brief intro sentence, then organized sections with ## headings.
- Use bullet lists for breakdowns and comparisons — never raw pipe tables.
- Keep bullet items concise: "**Mass**: 22 tickets (71%)" style.
- End with a 1–2 sentence insight under a ## Key Insight heading.

## HTML artifact rules
- When a chart would help understand the data, generate a self-contained HTML artifact
  and place it at the VERY END of your response inside a ```html ... ``` code block.
- Must be a complete page: <!DOCTYPE html> ... </html>
- Load Chart.js from CDN: <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
- Page styles: body { margin:0; padding:24px; background:#0f172a; color:#f1f5f9; font-family:system-ui,sans-serif; }
- h2 style: color:#f1f5f9; font-size:1rem; font-weight:600; margin:0 0 6px;
- p.summary style: color:#94a3b8; font-size:0.8rem; margin:0 0 16px; line-height:1.5;
- Include a styled <h2> title and a <p class="summary"> paragraph ABOVE the chart
- Chart canvas max-height: 360px
- Dataset colors (use in order): #6366f1, #10b981, #f59e0b, #f43f5e, #3b82f6, #a855f7, #14b8a6
- For bar charts use borderRadius:4; for pie/doughnut charts use hoverOffset:8
- ALWAYS set these Chart.js global options for visibility on dark background:
    plugins: {
      legend: { labels: { color: '#cbd5e1', font: { size: 12 } } }
    },
    scales: {   // (only for bar/line charts, not pie/doughnut)
      x: {
        ticks: { color: '#94a3b8', font: { size: 11 } },
        grid:  { color: 'rgba(148,163,184,0.12)' },
        border:{ color: 'rgba(148,163,184,0.2)' }
      },
      y: {
        ticks: { color: '#94a3b8', font: { size: 11 } },
        grid:  { color: 'rgba(148,163,184,0.12)' },
        border:{ color: 'rgba(148,163,184,0.2)' }
      }
    }
- Do NOT use external images or fonts — only the Chart.js CDN script

Only generate an HTML artifact when a chart genuinely adds value (distributions, comparisons, trends).
For simple factual answers, skip the artifact.
"""


def _make_tools() -> list:
    def stats() -> str:
        return json.dumps(get_ticket_stats(), default=str)

    def tickets(limit: int = 20) -> str:
        return json.dumps(get_tickets(limit), default=str)

    def filtered(field: str, value: str, limit: int = 30) -> str:
        return json.dumps(filter_tickets(field, value, limit), default=str)

    def priority() -> str:
        return json.dumps(get_priority_breakdown(), default=str)

    return [
        StructuredTool.from_function(
            stats,
            name="get_stats",
            description=(
                "Get aggregated statistics over all tickets: total count, avg priority, "
                "breakdowns by segment, request_type, sentiment, language, city, country."
            ),
        ),
        StructuredTool.from_function(
            tickets,
            name="get_tickets",
            description=(
                "Get a list of tickets from the database. "
                "Optional 'limit' (default 20). Returns segment, city, request_type, "
                "sentiment, priority, language, summary per ticket."
            ),
        ),
        StructuredTool.from_function(
            filtered,
            name="filter_tickets",
            description=(
                "Filter tickets by a field+value pair. "
                "Valid fields: city, country, segment, request_type, sentiment, language, gender, region. "
                "Example: field='sentiment', value='Негативный'."
            ),
        ),
        StructuredTool.from_function(
            priority,
            name="get_priority_breakdown",
            description="Get count of tickets at each priority level 1–10.",
        ),
    ]


def _parse_response(content: str) -> dict:
    html_artifact = None
    m = re.search(r"```html\s*(<!DOCTYPE\s+html.*?</html>)\s*```", content, re.DOTALL | re.IGNORECASE)
    if not m:
        m = re.search(r"```html\s*(.*?)\s*```", content, re.DOTALL)
    if m:
        html_artifact = m.group(1).strip()
        content = content[: m.start()].strip()
    return {"answer": content, "chart_data": None, "html_artifact": html_artifact}


def _tool_preview(name: str, raw: str) -> str:
    """Create a compact human-readable preview of a tool result."""
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return f"{len(data)} records returned"
        if isinstance(data, dict):
            if "total" in data:
                parts = [f"{data['total']} tickets"]
                if "avg_priority" in data:
                    parts.append(f"avg priority {data['avg_priority']}")
                top_segment = next(iter(data.get("by_segment", {})), None)
                if top_segment:
                    parts.append(f"top segment: {top_segment}")
                return " · ".join(parts)
            if "error" in data:
                return f"Error: {data['error']}"
            return "  ·  ".join(f"{k}: {v}" for k, v in list(data.items())[:4] if not isinstance(v, dict))
    except Exception:
        pass
    return raw[:120]


def _make_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=settings.hf_token,
        model="openai/gpt-oss-120b",
        temperature=0,
    )


# ── Streaming entry point ──────────────────────────────────────────────────────

def stream_agent(question: str, session_id: str | None = None) -> Generator[dict, None, None]:
    """
    Generator that yields SSE event dicts as the agent reasons step by step:
      {"type": "thinking", "text": "..."}         — initial thought (if any)
      {"type": "tool_start", "name": "...", "args": {...}}
      {"type": "tool_result", "name": "...", "preview": "..."}
      {"type": "done", "answer": "...", "html_artifact": "..."|null}
      {"type": "error", "message": "..."}
    """
    tools = _make_tools()
    agent = create_react_agent(_make_llm(), tools, prompt=SYSTEM_PROMPT)
    final_content = ""

    try:
        for chunk in agent.stream({"messages": [("user", question)]}):
            # Agent turn: either tool calls or the final answer
            if "agent" in chunk:
                agent_msg = chunk["agent"]["messages"][-1]
                tool_calls = getattr(agent_msg, "tool_calls", None)
                if tool_calls:
                    for tc in tool_calls:
                        yield {
                            "type": "tool_start",
                            "name": tc["name"],
                            "args": tc.get("args", {}),
                        }
                elif agent_msg.content:
                    final_content = agent_msg.content

            # Tool execution results
            elif "tools" in chunk:
                for msg in chunk["tools"]["messages"]:
                    yield {
                        "type": "tool_result",
                        "name": msg.name,
                        "preview": _tool_preview(msg.name, msg.content),
                    }

    except Exception as exc:
        yield {"type": "error", "message": str(exc)}
        return

    parsed = _parse_response(final_content)
    yield {
        "type": "done",
        "answer": parsed["answer"],
        "html_artifact": parsed["html_artifact"],
    }


# ── Blocking entry point (backward compat) ────────────────────────────────────

def run_agent(question: str, session_id: str | None = None) -> dict:
    tools = _make_tools()
    agent = create_react_agent(_make_llm(), tools, prompt=SYSTEM_PROMPT)
    try:
        result = agent.invoke({"messages": [("user", question)]})
        final = result["messages"][-1].content
    except Exception as exc:
        return {"answer": f"Sorry, I could not process your question. ({exc})", "chart_data": None, "html_artifact": None}
    return _parse_response(final)
