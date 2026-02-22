"""
FastMCP server — exposes the tickets_enriched PostgreSQL table as MCP tools.

Schema (tickets_enriched):
  ticket_id UUID PK, gender, birth_date, description, attachments,
  segment, country, region, city, street, house,
  latitude, longitude,
  request_type, sentiment, priority (1-10), language, summary

No session_id — the DB holds a single enriched dataset.
"""
from fastmcp import FastMCP
from sqlalchemy import create_engine, text

from app.core.config import settings

mcp = FastMCP(
    "FIRE Database",
    instructions=(
        "Query the bank's enriched customer support ticket database. "
        "Use these tools to answer questions about the ticket data."
    ),
)

_engine = create_engine(settings.database_url, pool_pre_ping=True)


def _query(sql: str, params: dict | None = None) -> list[dict]:
    """Execute a raw SQL query and return rows as plain dicts."""
    with _engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        cols = list(result.keys())
        return [dict(zip(cols, row)) for row in result.fetchall()]


# ── tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_ticket_stats() -> dict:
    """
    Return aggregated statistics over all tickets in the database.
    Includes total count, breakdowns by segment, request_type, sentiment,
    language, city, country, and the average priority score.
    """
    totals = _query("""
        SELECT COUNT(*)::int AS total, AVG(priority)::numeric(4,1) AS avg_priority
        FROM tickets_enriched
    """)
    row = totals[0] if totals else {}

    def dist(col: str) -> dict:
        r = _query(
            f"SELECT {col}, COUNT(*)::int AS n FROM tickets_enriched "
            f"WHERE {col} IS NOT NULL GROUP BY {col} ORDER BY n DESC"
        )
        return {str(r_[col]): r_["n"] for r_ in r}

    return {
        "total":           row.get("total", 0),
        "avg_priority":    float(row.get("avg_priority") or 0),
        "by_sentiment":    dist("sentiment"),
        "by_segment":      dist("segment"),
        "by_request_type": dist("request_type"),
        "by_language":     dist("language"),
        "by_city":         dist("city"),
        "by_country":      dist("country"),
    }


@mcp.tool()
def get_tickets(limit: int = 30) -> list[dict]:
    """
    Return up to `limit` tickets from the database (description omitted).
    Fields: ticket_id, gender, segment, city, country, request_type,
    sentiment, priority, language, summary.
    """
    return _query("""
        SELECT ticket_id::text, gender, segment, city, country,
               request_type, sentiment, priority, language, summary
        FROM tickets_enriched
        LIMIT :limit
    """, {"limit": limit})


@mcp.tool()
def filter_tickets(field: str, value: str, limit: int = 50) -> list[dict]:
    """
    Return tickets where `field` equals `value` (case-insensitive).
    Valid fields: city, country, segment, request_type, sentiment, language, gender, region.
    Returns ticket_id, segment, city, request_type, sentiment, priority, language, summary.
    """
    ALLOWED = {"city", "country", "segment", "request_type", "sentiment", "language", "gender", "region"}
    if field not in ALLOWED:
        return [{"error": f"field must be one of {sorted(ALLOWED)}"}]

    return _query(f"""
        SELECT ticket_id::text, segment, city, country,
               request_type, sentiment, priority, language, summary
        FROM tickets_enriched
        WHERE LOWER({field}::text) = LOWER(:value)
        LIMIT :limit
    """, {"value": value, "limit": limit})


@mcp.tool()
def get_priority_breakdown() -> list[dict]:
    """
    Return the count of tickets at each priority level (1–10),
    useful for understanding urgency distribution.
    """
    return _query("""
        SELECT priority, COUNT(*)::int AS count
        FROM tickets_enriched
        WHERE priority IS NOT NULL
        GROUP BY priority
        ORDER BY priority
    """)
