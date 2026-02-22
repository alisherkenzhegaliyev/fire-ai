"""
POST /api/upload

Full pipeline:
  CSV → NLP enrichment → 2GIS geocoding → business-logic assignment → PostgreSQL
"""
import asyncio
import logging
import time
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import engine
from app.modules.nlp.analyzer import analyze_ticket, CONCURRENCY
from app.modules.business.geo_filter import resolve_office_by_distance
from app.modules.business.assignment import RoundRobinState, pick_manager
from app.services.csv_parser import parse_csv
from app.services.geocoder_2gis import geocode_batch
from app.services.language_detector import detect_language
from app.store import save_session

log = logging.getLogger(__name__)
router = APIRouter()

MAX_NLP_TICKETS = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_managers() -> list[dict]:
    """Load managers from DB and normalise skills to a set of uppercase strings."""
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM managers")).mappings().all()
    managers = []
    for r in rows:
        raw_skills = r.get("skills") or ""
        skills = [s.strip().upper() for s in str(raw_skills).split(",") if s.strip()]
        managers.append({
            "manager_id": str(r["manager_id"]),
            "full_name": r["full_name"],
            "position": r.get("position") or "",
            "office": r.get("office") or "",
            "skills": skills,
            "workload": int(r.get("active_tickets_count") or 0),
        })
    return managers


def _load_offices() -> dict:
    """Load business_units from DB and return as dict keyed by office name."""
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM business_units")).mappings().all()
    offices = {}
    for r in rows:
        name = r["office"]
        offices[name] = {
            "office": name,
            "address": r.get("address") or "",
            "latitude": float(r["latitude"]) if r.get("latitude") is not None else None,
            "longitude": float(r["longitude"]) if r.get("longitude") is not None else None,
        }
    return offices


def _persist_to_db(tickets: list[dict]) -> None:
    """Upsert enriched+assigned tickets into tickets_final_enriched."""
    with engine.begin() as conn:
        # Ensure the table has assignment columns (idempotent)
        for col in ("assigned_manager_name", "assigned_manager_level",
                    "assigned_office", "assigned_office_address"):
            conn.execute(text(
                f"ALTER TABLE tickets_final_enriched ADD COLUMN IF NOT EXISTS {col} TEXT"
            ))

        for t in tickets:
            conn.execute(text("""
                INSERT INTO tickets_final_enriched (
                    customer_guid,
                    gender,
                    date_of_birth,
                    description,
                    attachments,
                    client_segment,
                    country,
                    region,
                    city,
                    street,
                    building,
                    request_type,
                    sentiment,
                    priority,
                    language,
                    summary,
                    next_actions,
                    lat,
                    lon,
                    assigned_manager_name,
                    assigned_manager_level,
                    assigned_office,
                    assigned_office_address
                ) VALUES (
                    :customer_guid,
                    :gender,
                    :date_of_birth,
                    :description,
                    :attachments,
                    :client_segment,
                    :country,
                    :region,
                    :city,
                    :street,
                    :building,
                    :request_type,
                    :sentiment,
                    :priority,
                    :language,
                    :summary,
                    :next_actions,
                    :lat,
                    :lon,
                    :assigned_manager_name,
                    :assigned_manager_level,
                    :assigned_office,
                    :assigned_office_address
                )
                ON CONFLICT (customer_guid) DO UPDATE SET
                    request_type            = EXCLUDED.request_type,
                    sentiment               = EXCLUDED.sentiment,
                    priority                = EXCLUDED.priority,
                    language                = EXCLUDED.language,
                    summary                 = EXCLUDED.summary,
                    next_actions            = EXCLUDED.next_actions,
                    lat                     = EXCLUDED.lat,
                    lon                     = EXCLUDED.lon,
                    assigned_manager_name   = EXCLUDED.assigned_manager_name,
                    assigned_manager_level  = EXCLUDED.assigned_manager_level,
                    assigned_office         = EXCLUDED.assigned_office,
                    assigned_office_address = EXCLUDED.assigned_office_address
            """), {
                "customer_guid":          t.get("customer_guid") or str(uuid.uuid4()),
                "gender":                 t.get("gender") or "",
                "date_of_birth":          t.get("date_of_birth") or "",
                "description":            t.get("description") or "",
                "attachments":            t.get("attachments") or "",
                "client_segment":         t.get("segment") or "",
                "country":                t.get("country") or "",
                "region":                 t.get("region") or "",
                "city":                   t.get("city") or "",
                "street":                 t.get("street") or "",
                "building":               t.get("building_number") or "",
                "request_type":           t.get("request_type") or "",
                "sentiment":              t.get("sentiment") or "",
                "priority":               t.get("priority_score"),
                "language":               t.get("language") or "",
                "summary":                t.get("summary") or "",
                "next_actions":           t.get("next_actions") or "",
                "lat":                    t.get("latitude"),
                "lon":                    t.get("longitude"),
                "assigned_manager_name":  t.get("assigned_manager_name"),
                "assigned_manager_level": t.get("assigned_manager_level"),
                "assigned_office":        t.get("assigned_office_name"),
                "assigned_office_address":t.get("assigned_office_address"),
            })


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

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

    if not tickets:
        raise HTTPException(
            status_code=422,
            detail="No ticket rows found. Make sure the CSV has a 'Description' column.",
        )

    total = min(len(tickets), MAX_NLP_TICKETS)
    tickets = tickets[:total]

    # ── 1. NLP enrichment ───────────────────────────────────────────────────
    log.info("NLP: processing %d tickets in parallel (concurrency=%d) …", total, CONCURRENCY)
    t0 = time.perf_counter()

    nlp_results = await asyncio.gather(
        *[analyze_ticket(t["description"], t.get("segment", "Mass"), index=i, total=total)
          for i, t in enumerate(tickets, start=1)]
    )

    enriched: list[dict] = [
        {
            **ticket,
            "request_type":  nlp["request_type"],
            "sentiment":     nlp["sentiment"],
            "priority_score":nlp["priority_score"],
            "language":      detect_language(ticket["description"]),
            "summary":       nlp["summary"],
            "next_actions":  nlp["next_actions"],
            "infer_time_ms": nlp["infer_time_ms"],
        }
        for ticket, nlp in zip(tickets, nlp_results)
    ]
    nlp_total_time = round(time.perf_counter() - t0, 2)
    nlp_avg_time = round(
        sum(t["infer_time_ms"] for t in enriched) / total / 1000, 2
    ) if total > 0 else 0
    log.info("NLP done in %.1fs (avg %.2fs/ticket)", nlp_total_time, nlp_avg_time)

    # ── 2. Geocoding ────────────────────────────────────────────────────────
    log.info("Geocoding %d tickets via 2GIS …", total)
    t1 = time.perf_counter()
    enriched = await geocode_batch(enriched)   # sets latitude/longitude
    log.info("Geocoding done in %.1fs", time.perf_counter() - t1)

    # ── 3. Load managers & offices from DB ──────────────────────────────────
    managers = _load_managers()
    offices = _load_offices()
    log.info("Loaded %d managers across %d offices", len(managers), len(offices))

    # ── 4. Business-logic assignment ────────────────────────────────────────
    rr = RoundRobinState()
    ok = fail = unmapped = 0

    for t in enriched:
        office_id = resolve_office_by_distance(t, offices)

        if not office_id:
            unmapped += 1
            log.warning("UNMAPPED %s — no coords", t.get("customer_guid"))
            t["assigned_manager_id"] = None
            t["assigned_manager_name"] = None
            t["assigned_manager_level"] = None
            t["assigned_office_id"] = None
            t["assigned_office_name"] = None
            t["assigned_office_address"] = None
            continue

        manager, resolved_office = pick_manager(t, office_id, managers, offices, rr)

        if not manager:
            fail += 1
            log.warning("FAIL %s — no eligible manager in any office", t.get("customer_guid"))
            t["assigned_manager_id"] = None
            t["assigned_manager_name"] = None
            t["assigned_manager_level"] = None
            t["assigned_office_id"] = None
            t["assigned_office_name"] = resolved_office
            t["assigned_office_address"] = (offices.get(resolved_office) or {}).get("address")
        else:
            ok += 1
            log.info(
                "OK %s → %s (%s)",
                t.get("customer_guid"), manager["full_name"], resolved_office,
            )
            t["assigned_manager_id"] = None
            t["assigned_manager_name"] = manager["full_name"]
            t["assigned_manager_level"] = manager["position"]
            t["assigned_office_id"] = None
            t["assigned_office_name"] = resolved_office
            t["assigned_office_address"] = (offices.get(resolved_office) or {}).get("address")

    log.info("Assignment — OK:%d  FAIL:%d  UNMAPPED:%d / %d", ok, fail, unmapped, total)

    # ── 5. Persist to PostgreSQL ─────────────────────────────────────────────
    log.info("Persisting %d tickets to tickets_final_enriched …", total)
    _persist_to_db(enriched)
    log.info("DB persist done.")

    # ── 6. Save in-memory session for agent queries ──────────────────────────
    session_id = str(uuid.uuid4())
    save_session(session_id, {
        "tickets":  enriched,
        "managers": managers,
    })

    return JSONResponse(content={
        "session_id":     session_id,
        "ticket_count":   len(enriched),
        "manager_count":  len(managers),
        "status":         "success",
        "nlp_total_time": nlp_total_time,
        "nlp_avg_time":   nlp_avg_time,
    })
