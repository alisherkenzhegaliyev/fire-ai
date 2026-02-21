"""
POST /api/upload

Accepts a CSV file, runs NLP on each ticket, stores everything
in the in-memory session store, and returns the session metadata.
"""
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

    enriched: list[dict] = []
    for i, ticket in enumerate(tickets[:MAX_NLP_TICKETS], start=1):
        nlp = analyze_ticket(ticket["description"], index=i, total=total)
        elapsed = time.perf_counter() - t_all
        avg = elapsed / i
        log.info("Progress: %d/%d done — %.1fs elapsed, avg %.1fs/ticket, est %.0fs remaining",
                 i, total, elapsed, avg, avg * (total - i))
        enriched.append({
            **ticket,
            "request_type": nlp["request_type"],
            "sentiment": nlp["sentiment"],
            "priority_score": nlp["priority_score"],
            "language": nlp["language"],
            "summary": nlp["summary"],
            "next_actions": nlp["next_actions"],
            # assignment — not done yet, null stubs
            "assigned_manager_id": None,
            "assigned_manager_name": None,
            "assigned_office_id": None,
            "assigned_office_name": None,
        })

    log.info("All %d tickets processed in %.1fs total", total, time.perf_counter() - t_all)

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
    })