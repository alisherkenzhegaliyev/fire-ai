"""Competency filter — applies cascading hard-skill rules to find eligible managers."""

LANG_KZ = "KZ"
LANG_ENG = "ENG"


def _is_chief(position: str) -> bool:
    p = (position or "").strip().lower()
    return p in ("chiefspecialist", "chief specialist", "главный специалист")


def filter_eligible_managers(ticket: dict, office_id: str, managers: list[dict]) -> list[dict]:
    """
    Filter managers for a given office using cumulative skill rules.

    managers must have:
      - 'skills': list of uppercase strings (e.g. ["VIP", "KZ", "ENG"])
      - 'office': office name matching office_id
      - 'is_active' (optional, defaults True): inactive managers are excluded
    """
    # 1. Office match (case-insensitive) + active check
    candidates = [
        m for m in managers
        if (m.get("office") or "").upper() == office_id.upper()
        and m.get("is_active", True)
    ]

    # 2. VIP/Priority segment OR priority >= 8 → manager needs VIP skill
    segment = (ticket.get("segment") or ticket.get("client_segment") or "").strip()
    priority = int(ticket.get("priority_score") or ticket.get("priority") or 0)
    if segment in ("VIP", "Priority") or priority >= 8:
        candidates = [m for m in candidates if "VIP" in (m.get("skills") or [])]

    # 3. DataChange request type → ChiefSpecialist only
    if (ticket.get("request_type") or "") == "DataChange":
        candidates = [m for m in candidates if _is_chief(m.get("position") or "")]

    # 4. Language — hard requirement (no soft fallback)
    lang = (ticket.get("language") or "RU").strip().upper()
    if lang == LANG_KZ:
        candidates = [m for m in candidates if LANG_KZ in (m.get("skills") or [])]
    elif lang == LANG_ENG:
        candidates = [m for m in candidates if LANG_ENG in (m.get("skills") or [])]

    return candidates
