"""
Direct database routes — read from tickets_final_enriched without a session.
"""
from collections import Counter

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import engine

router = APIRouter()


def _query(sql: str) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).mappings().all()
        return [dict(r) for r in rows]


def _distribution(values: list, total: int) -> list[dict]:
    counts = Counter(str(v) for v in values if v is not None)
    return [
        {
            "label": label,
            "count": count,
            "percentage": round(count / total * 100, 1) if total else 0.0,
        }
        for label, count in sorted(counts.items(), key=lambda x: -x[1])
    ]


@router.get("/db/analytics")
def get_db_analytics():
    rows = _query("""
        SELECT
            client_segment   AS segment,
            request_type,
            sentiment,
            language,
            city,
            priority::int    AS priority,
            assigned_manager_name
        FROM tickets_final_enriched
    """)

    if not rows:
        return JSONResponse(content={
            "total_tickets": 0,
            "total_managers": 0,
            "assigned_count": 0,
            "unassigned_count": 0,
            "by_segment": [],
            "by_request_type": [],
            "by_sentiment": [],
            "by_language": [],
            "by_office": [],
            "avg_priority_score": 0.0,
        })

    total = len(rows)
    priorities = [r["priority"] for r in rows if r["priority"] is not None]
    avg_priority = round(sum(priorities) / len(priorities), 2) if priorities else 0.0
    assigned_count = sum(
        1 for r in rows
        if r.get("assigned_manager_name") and str(r["assigned_manager_name"]).strip()
    )

    return JSONResponse(content={
        "total_tickets": total,
        "total_managers": 0,
        "assigned_count": assigned_count,
        "unassigned_count": total - assigned_count,
        "by_segment": _distribution([r["segment"] for r in rows], total),
        "by_request_type": _distribution([r["request_type"] for r in rows], total),
        "by_sentiment": _distribution([r["sentiment"] for r in rows], total),
        "by_language": _distribution([r["language"] for r in rows], total),
        "by_office": _distribution([r["city"] for r in rows], total),
        "avg_priority_score": avg_priority,
    })


@router.get("/db/tickets")
def get_db_tickets():
    rows = _query("""
        SELECT
            customer_guid::text                        AS id,
            COALESCE(gender, '')                       AS gender,
            COALESCE(date_of_birth::text, '')          AS date_of_birth,
            COALESCE(description, '')                  AS description,
            COALESCE(attachments, '')                  AS attachments,
            COALESCE(client_segment, '')               AS segment,
            COALESCE(country, '')                      AS country,
            COALESCE(region, '')                       AS region,
            COALESCE(city, '')                         AS city,
            COALESCE(street, '')                       AS street,
            COALESCE(building, '')                     AS building_number,
            lat::float                                 AS latitude,
            lon::float                                 AS longitude,
            COALESCE(request_type, '')                 AS request_type,
            COALESCE(sentiment, '')                    AS sentiment,
            priority::int                              AS priority_score,
            COALESCE(language, '')                     AS language,
            COALESCE(summary, '')                      AS summary,
            COALESCE(next_actions, '')                 AS next_actions,
            COALESCE(assigned_manager_name, '')        AS assigned_manager_name,
            COALESCE(assigned_manager_level, '')       AS assigned_manager_level,
            COALESCE(assigned_office, '')              AS assigned_office_name,
            COALESCE(assigned_office_address, '')      AS assigned_office_address
        FROM tickets_final_enriched
        ORDER BY priority DESC NULLS LAST
    """)

    tickets = [
        {
            **{k: (float(v) if isinstance(v, float) else v) for k, v in row.items()},
            "customer_guid":      row.get("id"),
            "assigned_manager_id":None,
            "assigned_office_id": None,
            "session_id":         "db",
            "created_at":         None,
        }
        for row in rows
    ]

    return JSONResponse(content=tickets)
