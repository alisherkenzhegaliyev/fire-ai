"""
GET /api/managers?session_id=xxx   — from in-memory session
GET /api/managers/db               — directly from PostgreSQL managers table
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import engine
from app.store import get_session

router = APIRouter()


@router.get("/managers/db")
def get_managers_from_db():
    """Return all managers from the PostgreSQL managers table (DB-browse mode)."""
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM managers ORDER BY full_name")).mappings().all()
    result = []
    for r in rows:
        raw_skills = r.get("skills") or ""
        skills = [s.strip().upper() for s in str(raw_skills).split(",") if s.strip()]
        result.append({
            "id": str(r["manager_id"]),
            "fullName": r["full_name"],
            "position": r.get("position") or "Specialist",
            "skills": skills,
            "businessUnit": r.get("office") or "",
            "workload": int(r.get("active_tickets_count") or 0),
            "sessionId": "db",
        })
    return JSONResponse(content=result)


@router.get("/managers")
def get_managers(session_id: str = Query(...)):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return JSONResponse(content=session["managers"])