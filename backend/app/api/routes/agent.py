"""
POST /api/agent/query

Accepts a natural language question + session_id,
calls the Gemini visualizer, returns answer + optional chart payload.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.store import get_session
from app.modules.agent.visualizer import handle_query

router = APIRouter()


class AgentQueryRequest(BaseModel):
    question: str
    session_id: str


@router.post("/agent/query")
def agent_query(body: AgentQueryRequest):
    session = get_session(body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    result = handle_query(
        question=body.question,
        tickets=session["tickets"],
        managers=session["managers"],
    )

    return JSONResponse(content={
        "answer": result["answer"],
        "chart_data": result["chart_data"],
    })