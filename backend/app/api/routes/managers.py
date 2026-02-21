"""
GET /api/managers?session_id=xxx

Returns manager list from the in-memory session store.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.store import get_session

router = APIRouter()


@router.get("/managers")
def get_managers(session_id: str = Query(...)):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return JSONResponse(content=session["managers"])