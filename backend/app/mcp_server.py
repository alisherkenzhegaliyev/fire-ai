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

_ALLOWED_FIELDS = {
    "client_segment", "request_type", "sentiment", "language",
    "assigned_manager_level", "assigned_office",
    "city", "country", "region", "gender",
    "assigned_manager_name",
}


def _sanitize(v):
    """Strip NUL bytes from string values (can appear in CSV-imported text columns)."""
    if isinstance(v, str):
        return v.replace("\x00", "")
    return v


def _query(sql: str, params: dict | None = None) -> list[dict]:
    """Execute a raw SQL query and return rows as plain dicts."""
    with _engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        cols = list(result.keys())
        return [
            {k: _sanitize(v) for k, v in zip(cols, row)}
            for row in result.fetchall()
        ]


# ── tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_ticket_stats() -> dict:
    """
    Return aggregated statistics over all tickets in the database.
    Includes total count, assigned/unassigned counts, avg priority, and breakdowns
    by client_segment, request_type, sentiment, language, assigned_manager_level,
    and assigned_office. For geo or city breakdowns use get_cross_breakdown instead.
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
        "total":             row.get("total", 0),
        "assigned_count":    assigned_count[0]["n"] if assigned_count else 0,
        "unassigned_count":  (row.get("total", 0) or 0) - (assigned_count[0]["n"] if assigned_count else 0),
        "avg_priority":      float(row.get("avg_priority") or 0),
        "by_sentiment":      dist("sentiment"),
        "by_segment":        dist("client_segment"),
        "by_request_type":   dist("request_type"),
        "by_language":       dist("language"),
        "by_assigned_level": dist("assigned_manager_level"),
        "by_assigned_office": dist("assigned_office"),
    }


@mcp.tool()
def get_cross_breakdown(group_by: str, secondary_group: str) -> list[dict]:
    """
    Return a cross-tabulation: ticket counts grouped by two fields simultaneously.
    Use this for questions like 'sentiment by segment', 'request type by language', etc.
    Each row has the two field values and a 'count'.
    Valid fields: client_segment, request_type, sentiment, language,
    assigned_office, assigned_manager_level, gender, country, region, city.
    Example: group_by='client_segment', secondary_group='sentiment'
    """
    ALLOWED = {
        "client_segment", "request_type", "sentiment", "language",
        "assigned_office", "assigned_manager_level", "gender",
        "country", "region", "city",
    }
    if group_by not in ALLOWED:
        return [{"error": f"group_by must be one of {sorted(ALLOWED)}"}]
    if secondary_group not in ALLOWED:
        return [{"error": f"secondary_group must be one of {sorted(ALLOWED)}"}]

    return _query(f"""
        SELECT {group_by}, {secondary_group}, COUNT(*)::int AS count
        FROM {_TABLE}
        WHERE {group_by} IS NOT NULL AND {group_by} != ''
          AND {secondary_group} IS NOT NULL AND {secondary_group} != ''
        GROUP BY {group_by}, {secondary_group}
        ORDER BY {group_by}, count DESC
    """)


@mcp.tool()
def get_tickets(limit: int = 30) -> list[dict]:
    """
    Return up to `limit` tickets from the database (max 50; description and next_actions omitted).
    Fields returned: customer_guid, gender, date_of_birth, client_segment, country,
    region, city, request_type, sentiment, priority, language,
    summary, assigned_manager_name, assigned_manager_level,
    assigned_office, assigned_office_address.
    """
    return _query(f"""
        SELECT customer_guid::text, gender, date_of_birth, client_segment, country,
               region, city,
               request_type, sentiment, priority, language,
               summary,
               assigned_manager_name, assigned_manager_level,
               assigned_office, assigned_office_address
        FROM {_TABLE}
        LIMIT :limit
    """, {"limit": min(limit, 50)})


@mcp.tool()
def filter_tickets(field: str, value: str, limit: int = 30) -> list[dict]:
    """
    Return tickets where `field` equals `value` (case-insensitive), up to `limit` rows (max 50).
    Valid fields: city, country, region, client_segment, request_type, sentiment,
    language, gender, assigned_manager_name, assigned_manager_level, assigned_office.
    Returns key fields only (no description, summary, or next_actions).
    For aggregated breakdowns prefer get_cross_breakdown instead.
    """
    if field not in _ALLOWED_FIELDS:
        return [{"error": f"field must be one of {sorted(_ALLOWED_FIELDS)}"}]

    return _query(f"""
        SELECT customer_guid::text, gender, date_of_birth, client_segment, country,
               region, city, request_type, sentiment, priority, language,
               assigned_manager_name, assigned_manager_level,
               assigned_office, assigned_office_address
        FROM {_TABLE}
        WHERE LOWER({field}::text) = LOWER(:value)
        LIMIT :limit
    """, {"value": value, "limit": min(limit, 50)})


@mcp.tool()
def get_age_stats(filter_field: str | None = None, filter_value: str | None = None) -> dict:
    """
    Return average, min, and max client age (computed from date_of_birth).
    Optionally filter by one field+value pair before computing.
    Valid filter_field values: assigned_office, assigned_manager_name, client_segment,
    request_type, sentiment, language, gender, city, country, region.
    Example: filter_field='assigned_office', filter_value='Астана'
    Returns: {"avg_age": float, "min_age": int, "max_age": int, "count": int}
    """
    where = "WHERE date_of_birth IS NOT NULL"
    params: dict = {}

    if filter_field and filter_value:
        ALLOWED = {
            "assigned_office", "assigned_manager_name", "client_segment",
            "request_type", "sentiment", "language", "gender", "city", "country", "region",
        }
        if filter_field not in ALLOWED:
            return {"error": f"filter_field must be one of {sorted(ALLOWED)}"}
        where += f" AND LOWER({filter_field}::text) = LOWER(:fv)"
        params["fv"] = filter_value

    rows = _query(f"""
        SELECT
            ROUND(AVG(DATE_PART('year', AGE(NOW(), date_of_birth::date)))::numeric, 1)::float AS avg_age,
            MIN(DATE_PART('year', AGE(NOW(), date_of_birth::date)))::int                       AS min_age,
            MAX(DATE_PART('year', AGE(NOW(), date_of_birth::date)))::int                       AS max_age,
            COUNT(*)::int                                                                       AS count
        FROM {_TABLE}
        {where}
          AND date_of_birth::date > '1900-01-01'
          AND date_of_birth::date < NOW()::date
    """, params)
    return rows[0] if rows else {"avg_age": None, "min_age": None, "max_age": None, "count": 0}


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
