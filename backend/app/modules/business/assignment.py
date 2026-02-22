"""
Assignment module — round-robin between top-2 lowest-workload eligible managers,
with automatic fallback to neighboring offices when no eligible manager is found.
"""
from app.modules.business.competency_filter import filter_eligible_managers
from app.modules.business.geo_filter import sorted_offices_by_distance


class RoundRobinState:
    """Per-office toggle: alternates index 0/1 across assignments in a session."""

    def __init__(self):
        self._state: dict[str, int] = {}

    def next_index(self, office_id: str) -> int:
        idx = self._state.get(office_id, 0)
        self._state[office_id] = 1 - idx
        return idx


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
    3. Among candidates: sort by workload asc, take top-2, round-robin between them.
    4. Increment chosen manager's in-memory workload by 1.

    Returns (chosen_manager_dict | None, resolved_office_id).
    """
    candidates = filter_eligible_managers(ticket, office_id, managers)

    if not candidates:
        for other_id in sorted_offices_by_distance(office_id, offices):
            candidates = filter_eligible_managers(ticket, other_id, managers)
            if candidates:
                office_id = other_id
                break

    if not candidates:
        return None, office_id

    candidates.sort(key=lambda m: (m.get("workload", 0), str(m.get("manager_id", ""))))
    top2 = candidates[:2]
    chosen = top2[rr.next_index(office_id) % len(top2)]
    chosen["workload"] = chosen.get("workload", 0) + 1
    return chosen, office_id
