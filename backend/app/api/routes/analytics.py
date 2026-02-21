"""
GET /api/analytics?session_id=xxx

Computes aggregated statistics from the in-memory ticket list and returns them.
"""
from collections import Counter

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.store import get_session

router = APIRouter()


def _distribution(items: list[str]) -> list[dict]:
    total = len(items) or 1
    counts = Counter(items)
    return [
        {"label": label, "count": count, "percentage": round(count / total * 100, 1)}
        for label, count in sorted(counts.items(), key=lambda x: -x[1])
    ]


@router.get("/analytics")
def get_analytics(session_id: str = Query(...)):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    tickets: list[dict] = session["tickets"]
    managers: list[dict] = session["managers"]

    total = len(tickets)
    assigned = sum(1 for t in tickets if t.get("assigned_manager_id"))
    priorities = [t.get("priority_score", 5) for t in tickets]
    avg_priority = round(sum(priorities) / len(priorities), 1) if priorities else 0.0

    return JSONResponse(content={
        "total_tickets": total,
        "total_managers": len(managers),
        "assigned_count": assigned,
        "unassigned_count": total - assigned,
        "by_segment": _distribution([t.get("segment", "Mass") for t in tickets]),
        "by_request_type": _distribution([t.get("request_type", "") for t in tickets]),
        "by_sentiment": _distribution([t.get("sentiment", "") for t in tickets]),
        "by_language": _distribution([t.get("language", "RU") for t in tickets]),
        "by_office": _distribution([t["assigned_office_name"] for t in tickets if t.get("assigned_office_name")]),
        "avg_priority_score": avg_priority,
    })