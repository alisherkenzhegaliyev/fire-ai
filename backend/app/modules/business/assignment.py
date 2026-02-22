"""
Assignment module — hash-bucketed round-robin between top-2 lowest-workload eligible managers,
with automatic fallback to neighboring offices when no eligible manager is found.
"""
import hashlib
from typing import Optional, Tuple, Dict

from app.modules.business.competency_filter import filter_eligible_managers
from app.modules.business.geo_filter import sorted_offices_by_distance


class RoundRobinState:
    """
    Per-bucket alternation between the top-2 lowest-workload eligible managers.

    Bucket key: (office_id, is_vip, language, is_data_change)
    Each bucket independently tracks which manager was assigned last and how many
    tickets have been routed through it (used as the MD5 tiebreaker seed).
    """

    def __init__(self):
        self.last_assigned: Dict[Tuple, Optional[str]] = {}
        self._bucket_ticket_count: Dict[Tuple, int] = {}

    def _make_key(self, office_id: str, ticket: dict) -> Tuple:
        segment = (ticket.get("segment") or ticket.get("client_segment") or "").strip()
        is_vip = segment in ("VIP", "Priority")
        lang = (ticket.get("language") or "RU").upper()
        is_data = (ticket.get("request_type") or "") == "DataChange"
        return (office_id, is_vip, lang, is_data)

    def _sort_key(self, manager: dict, ticket_index: int) -> Tuple:
        m_id = str(manager.get("manager_id") or manager.get("id") or "")
        workload = manager.get("workload", 0)
        tiebreak = int(hashlib.md5(f"{m_id}:{ticket_index}".encode()).hexdigest(), 16) % (10 ** 9)
        return (workload, tiebreak)

    def choose_manager(self, office_id: str, ticket: dict, eligible: list) -> Optional[dict]:
        if not eligible:
            return None

        key = self._make_key(office_id, ticket)
        ticket_index = self._bucket_ticket_count.get(key, 0)
        self._bucket_ticket_count[key] = ticket_index + 1

        sorted_managers = sorted(eligible, key=lambda m: self._sort_key(m, ticket_index))
        top2 = sorted_managers[:2]

        last = self.last_assigned.get(key)
        if last is None or len(top2) == 1:
            chosen = top2[0]
        else:
            top2_ids = [str(m.get("manager_id") or m.get("id") or "") for m in top2]
            if last in top2_ids:
                next_idx = 1 - top2_ids.index(last)
                chosen = top2[next_idx]
            else:
                chosen = top2[0]

        self.last_assigned[key] = str(chosen.get("manager_id") or chosen.get("id") or "")
        return chosen


def pick_manager(
    ticket: dict,
    office_id: str,
    managers: list[dict],
    offices: dict,
    rr: RoundRobinState,
) -> tuple[dict | None, str]:
    """
    Select a manager for a ticket.

    1. Try the nearest office (office_id).
    2. If no eligible candidates, fall back to sorted neighboring offices.
    3. Among candidates: sort by workload asc + MD5 tiebreaker, take top-2,
       alternate between them per (office, vip, lang, data_change) bucket.
    4. Increment chosen manager's in-memory workload by 1.

    Returns (chosen_manager_dict | None, resolved_office_id).
    """
    # Spam tickets are never assigned to a manager
    if (ticket.get("request_type") or "").strip() == "Spam":
        return None, office_id

    candidates = filter_eligible_managers(ticket, office_id, managers)

    if not candidates:
        for other_id in sorted_offices_by_distance(office_id, offices):
            candidates = filter_eligible_managers(ticket, other_id, managers)
            if candidates:
                office_id = other_id
                break

    if not candidates:
        return None, office_id

    chosen = rr.choose_manager(office_id, ticket, candidates)
    if chosen is None:
        return None, office_id

    chosen["workload"] = chosen.get("workload", 0) + 1
    return chosen, office_id
