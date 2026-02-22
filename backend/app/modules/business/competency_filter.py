"""Competency filter — applies cascading hard-skill rules to find eligible managers."""


def _is_chief(position: str) -> bool:
    p = (position or "").strip().lower()
    return p in ("chiefspecialist", "chief specialist", "главный специалист")


def filter_eligible_managers(ticket: dict, office_id: str, managers: list[dict]) -> list[dict]:
    """
    Filter managers for a given office using cumulative skill rules.

    managers must have a 'skills' field that is a list of uppercase strings
    (e.g. ["VIP", "KZ", "ENG"]) and an 'office' field matching office_id.
    """
    # 1. Office match (case-insensitive)
    candidates = [m for m in managers if (m.get("office") or "").upper() == office_id.upper()]

    # 2. VIP/Priority segment OR priority >= 8 → manager needs VIP skill
    segment = (ticket.get("segment") or ticket.get("client_segment") or "").strip()
    priority = int(ticket.get("priority_score") or ticket.get("priority") or 0)
    if segment in ("VIP", "Priority") or priority >= 8:
        candidates = [m for m in candidates if "VIP" in (m.get("skills") or set())]

    # 3. DataChange request type → ChiefSpecialist only
    if (ticket.get("request_type") or "") == "DataChange":
        candidates = [m for m in candidates if _is_chief(m.get("position") or "")]

    # 4. Language — soft fallback: if nobody speaks the required language, keep all remaining
    lang = (ticket.get("language") or "RU").strip().upper()
    if lang == "KZ":
        lang_ok = [m for m in candidates if "KZ" in (m.get("skills") or set())]
        candidates = lang_ok if lang_ok else candidates
    elif lang == "ENG":
        lang_ok = [m for m in candidates if "ENG" in (m.get("skills") or set())]
        candidates = lang_ok if lang_ok else candidates

    return candidates
