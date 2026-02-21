"""
GET /api/tickets?session_id=xxx

Returns enriched ticket list from the in-memory session store.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.store import get_session

router = APIRouter()


@router.get("/tickets")
def get_tickets(session_id: str = Query(...)):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return JSONResponse(content=session["tickets"])