"""
POST /api/agent/query

Accepts a natural language question + optional session_id.
session_id is optional — if omitted, agent runs in test mode with no data.
Delegates to the LangGraph ReAct agent in app.modules.agent.graph.
"""
import json

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.modules.agent.graph import run_agent, stream_agent

router = APIRouter()


class AgentQueryRequest(BaseModel):
    question: str
    session_id: str | None = None


@router.post("/agent/query")
def agent_query(body: AgentQueryRequest, session_id: str | None = Query(default=None)):
    effective_session_id = body.session_id or session_id
    result = run_agent(body.question, effective_session_id)
    return JSONResponse(content={
        "answer": result["answer"],
        "chart_data": result["chart_data"],
        "html_artifact": result.get("html_artifact"),
    })


@router.post("/agent/query/stream")
def agent_query_stream(body: AgentQueryRequest, session_id: str | None = Query(default=None)):
    """SSE endpoint that streams reasoning steps as they happen."""
    effective_session_id = body.session_id or session_id

    def event_generator():
        for event in stream_agent(body.question, effective_session_id):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
