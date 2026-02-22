"""
FastMCP server — exposes the tickets_final_enriched PostgreSQL table as MCP tools.

Schema (tickets_final_enriched):
  customer_guid, gender, date_of_birth, description, attachments,
  client_segment, country, region, city, street, building,
  lat, lon,
  request_type, sentiment, priority (1-10), language, summary, next_actions,
  assigned_manager_name, assigned_manager_level, assigned_office, assigned_office_address

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
_TABLE = "tickets_final_enriched"


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
    Includes total count, breakdowns by client_segment, request_type, sentiment,
    language, city, country, assigned_manager_name, assigned_manager_level,
    assigned_office, and the average priority score.
    """
    totals = _query(f"""
        SELECT COUNT(*)::int AS total, AVG(priority)::numeric(4,1) AS avg_priority
        FROM {_TABLE}
    """)
    row = totals[0] if totals else {}

    def dist(col: str) -> dict:
        r = _query(
            f"SELECT {col}, COUNT(*)::int AS n FROM {_TABLE} "
            f"WHERE {col} IS NOT NULL AND {col} != '' GROUP BY {col} ORDER BY n DESC"
        )
        return {str(r_[col]): r_["n"] for r_ in r}

    assigned_count = _query(
        f"SELECT COUNT(*)::int AS n FROM {_TABLE} WHERE assigned_manager_name IS NOT NULL AND assigned_manager_name != ''"
    )

    return {
        "total":                   row.get("total", 0),
        "assigned_count":          assigned_count[0]["n"] if assigned_count else 0,
        "unassigned_count":        (row.get("total", 0) or 0) - (assigned_count[0]["n"] if assigned_count else 0),
        "avg_priority":            float(row.get("avg_priority") or 0),
        "by_sentiment":            dist("sentiment"),
        "by_segment":              dist("client_segment"),
        "by_request_type":         dist("request_type"),
        "by_language":             dist("language"),
        "by_city":                 dist("city"),
        "by_country":              dist("country"),
        "by_region":               dist("region"),
        "by_assigned_manager":     dist("assigned_manager_name"),
        "by_assigned_level":       dist("assigned_manager_level"),
        "by_assigned_office":      dist("assigned_office"),
    }


@mcp.tool()
def get_tickets(limit: int = 30) -> list[dict]:
    """
    Return up to `limit` tickets from the database (description omitted for brevity).
    Fields returned: customer_guid, gender, date_of_birth, client_segment, country,
    region, city, street, building, request_type, sentiment, priority, language,
    summary, next_actions, assigned_manager_name, assigned_manager_level,
    assigned_office, assigned_office_address.
    """
    return _query(f"""
        SELECT customer_guid::text, gender, date_of_birth, client_segment, country,
               region, city, street, building,
               request_type, sentiment, priority, language,
               summary, next_actions,
               assigned_manager_name, assigned_manager_level,
               assigned_office, assigned_office_address
        FROM {_TABLE}
        LIMIT :limit
    """, {"limit": limit})


@mcp.tool()
def filter_tickets(field: str, value: str, limit: int = 50) -> list[dict]:
    """
    Return tickets where `field` equals `value` (case-insensitive).
    Valid fields: city, country, region, client_segment, request_type, sentiment,
    language, gender, assigned_manager_name, assigned_manager_level, assigned_office.
    Returns all fields except description and attachments.
    """
    ALLOWED = {
        "city", "country", "region", "client_segment", "request_type",
        "sentiment", "language", "gender",
        "assigned_manager_name", "assigned_manager_level", "assigned_office",
    }
    if field not in ALLOWED:
        return [{"error": f"field must be one of {sorted(ALLOWED)}"}]

    return _query(f"""
        SELECT customer_guid::text, gender, date_of_birth, client_segment, country,
               region, city, street, building,
               request_type, sentiment, priority, language,
               summary, next_actions,
               assigned_manager_name, assigned_manager_level,
               assigned_office, assigned_office_address
        FROM {_TABLE}
        WHERE LOWER({field}::text) = LOWER(:value)
        LIMIT :limit
    """, {"value": value, "limit": limit})


@mcp.tool()
def get_priority_breakdown() -> list[dict]:
    """
    Return the count of tickets at each priority level (1–10),
    useful for understanding urgency distribution.
    """
    return _query(f"""
        SELECT priority, COUNT(*)::int AS count
        FROM {_TABLE}
        WHERE priority IS NOT NULL
        GROUP BY priority
        ORDER BY priority
    """)


@mcp.tool()
def get_manager_workloads() -> list[dict]:
    """
    Return each assigned manager's ticket count and their office,
    sorted by ticket count descending. Useful for workload analysis.
    """
    return _query(f"""
        SELECT assigned_manager_name, assigned_manager_level, assigned_office,
               COUNT(*)::int AS ticket_count
        FROM {_TABLE}
        WHERE assigned_manager_name IS NOT NULL AND assigned_manager_name != ''
        GROUP BY assigned_manager_name, assigned_manager_level, assigned_office
        ORDER BY ticket_count DESC
    """)
