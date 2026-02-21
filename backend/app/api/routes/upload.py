"""
POST /api/upload

Accepts a CSV file, runs NLP on each ticket, stores everything
in the in-memory session store, and returns the session metadata.
"""
import asyncio
import logging
import time
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services.csv_parser import parse_csv
from app.modules.nlp.analyzer import analyze_ticket
from app.store import save_session

log = logging.getLogger(__name__)
router = APIRouter()

MAX_NLP_TICKETS = 50


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    content = await file.read()

    try:
        parsed = parse_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    tickets: list[dict] = parsed["tickets"]
    managers: list[dict] = parsed["managers"]

    if not tickets:
        raise HTTPException(
            status_code=422,
            detail="No ticket rows found. Make sure the CSV has a 'Description' column.",
        )

    total = min(len(tickets), MAX_NLP_TICKETS)
    log.info("Starting NLP on %d tickets (of %d total) …", total, len(tickets))
    t_all = time.perf_counter()

    batch = tickets[:MAX_NLP_TICKETS]
    nlp_results = await asyncio.gather(
        *[analyze_ticket(t["description"], index=i, total=total) for i, t in enumerate(batch, start=1)]
    )

    enriched: list[dict] = [
        {
            **ticket,
            "request_type": nlp["request_type"],
            "sentiment": nlp["sentiment"],
            "priority_score": nlp["priority_score"],
            "language": nlp["language"],
            "summary": nlp["summary"],
            "next_actions": nlp["next_actions"],
            "infer_time_ms": nlp["infer_time_ms"],
            # assignment — not done yet, null stubs
            "assigned_manager_id": None,
            "assigned_manager_name": None,
            "assigned_office_id": None,
            "assigned_office_name": None,
        }
        for ticket, nlp in zip(batch, nlp_results)
    ]

    nlp_total_time = round(time.perf_counter() - t_all, 2)
    nlp_avg_time = round(sum(r["infer_time_ms"] for r in nlp_results) / total / 1000, 2) if total > 0 else 0
    log.info("All %d tickets processed in %.1fs total (avg %.2fs/ticket)", total, nlp_total_time, nlp_avg_time)

    session_id = str(uuid.uuid4())
    save_session(session_id, {
        "tickets": enriched,
        "managers": managers,
    })

    return JSONResponse(content={
        "session_id": session_id,
        "ticket_count": len(enriched),
        "manager_count": len(managers),
        "status": "success",
        "nlp_total_time": nlp_total_time,
        "nlp_avg_time": nlp_avg_time,
    })