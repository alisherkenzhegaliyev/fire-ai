"""
CSV Parser — reads an uploaded CSV file and returns raw ticket/manager/office rows.
No DB writes. Returns plain dicts for in-memory processing.
"""
import io
import uuid
from datetime import datetime, timezone

import pandas as pd


# ── Column name normalisation ─────────────────────────────────────────────────

def _norm(col: str) -> str:
    """Lowercase + strip + collapse spaces to underscore."""
    return col.strip().lower().replace(" ", "_")


# Maps normalised column → canonical field name
TICKET_COL_MAP = {
    "customer_guid": "customer_guid",
    "guid": "customer_guid",
    "gender": "gender",
    "пол": "gender",
    "date_of_birth": "date_of_birth",
    "dob": "date_of_birth",
    "дата_рождения": "date_of_birth",
    "segment": "segment",
    "сегмент": "segment",
    "description": "description",
    "описание": "description",
    "request": "description",
    "text": "description",
    "attachments": "attachments",
    "вложения": "attachments",
    "country": "country",
    "страна": "country",
    "region": "region",
    "регион": "region",
    "city": "city",
    "город": "city",
    "street": "street",
    "улица": "street",
    "building_number": "building_number",
    "building": "building_number",
    "дом": "building_number",
}

MANAGER_COL_MAP = {
    "full_name": "full_name",
    "fullname": "full_name",
    "name": "full_name",
    "имя": "full_name",
    "фио": "full_name",
    "position": "position",
    "должность": "position",
    "skills": "skills",
    "навыки": "skills",
    "business_unit": "business_unit",
    "businessunit": "business_unit",
    "office": "business_unit",
    "офис": "business_unit",
    "workload": "workload",
    "нагрузка": "workload",
    "current_workload": "workload",
}


def _rename(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    rename = {}
    for col in df.columns:
        key = _norm(col)
        if key in col_map:
            rename[col] = col_map[key]
    return df.rename(columns=rename)


# ── Public parse function ─────────────────────────────────────────────────────

def parse_csv(content: bytes) -> dict:
    """
    Parse raw CSV bytes.
    Tries to detect ticket rows by looking for a description-like column.
    Also looks for manager rows if a separate section / sheet exists.

    Returns:
        {
          "tickets": [dict, ...],
          "managers": [dict, ...],
        }
    """
    try:
        df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ValueError(f"Could not parse CSV: {exc}") from exc

    df_tickets = _rename(df.copy(), TICKET_COL_MAP)

    tickets = []
    if "description" in df_tickets.columns:
        for _, row in df_tickets.iterrows():
            r = row.to_dict()
            ticket = {
                "id": str(uuid.uuid4()),
                "customer_guid": r.get("customer_guid", str(uuid.uuid4())),
                "gender": r.get("gender", ""),
                "date_of_birth": r.get("date_of_birth", ""),
                "segment": _normalise_segment(r.get("segment", "Mass")),
                "description": r.get("description", ""),
                "attachments": r.get("attachments", ""),
                "country": r.get("country", ""),
                "region": r.get("region", ""),
                "city": r.get("city", ""),
                "street": r.get("street", ""),
                "building_number": r.get("building_number", ""),
                "latitude": None,
                "longitude": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if ticket["description"].strip():
                tickets.append(ticket)

    # Try to parse managers if columns match
    df_managers = _rename(df.copy(), MANAGER_COL_MAP)
    managers = []
    if "full_name" in df_managers.columns:
        for _, row in df_managers.iterrows():
            r = row.to_dict()
            raw_skills = r.get("skills", "")
            skills = [s.strip() for s in raw_skills.split(",") if s.strip()] if raw_skills else []
            managers.append({
                "id": str(uuid.uuid4()),
                "full_name": r.get("full_name", ""),
                "position": _normalise_position(r.get("position", "Specialist")),
                "skills": skills,
                "business_unit": r.get("business_unit", ""),
                "workload": int(r.get("workload", 0) or 0),
            })

    return {"tickets": tickets, "managers": managers}


def _normalise_segment(raw: str) -> str:
    mapping = {
        "vip": "VIP",
        "priority": "Priority",
        "приоритет": "Priority",
        "mass": "Mass",
        "масс": "Mass",
        "массовый": "Mass",
    }
    return mapping.get(raw.strip().lower(), "Mass")


def _normalise_position(raw: str) -> str:
    mapping = {
        "specialist": "Specialist",
        "специалист": "Specialist",
        "senior specialist": "SeniorSpecialist",
        "seniorspecialist": "SeniorSpecialist",
        "старший специалист": "SeniorSpecialist",
        "chief specialist": "ChiefSpecialist",
        "chiefspecialist": "ChiefSpecialist",
        "главный специалист": "ChiefSpecialist",
    }
    return mapping.get(raw.strip().lower(), "Specialist")