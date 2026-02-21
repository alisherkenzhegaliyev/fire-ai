"""
In-memory session store.
Holds enriched ticket data per session_id for the duration of the server process.
No persistence — purely for testing the AI module end-to-end.
"""
from typing import Any

_sessions: dict[str, dict[str, Any]] = {}


def save_session(session_id: str, data: dict[str, Any]) -> None:
    _sessions[session_id] = data


def get_session(session_id: str) -> dict[str, Any] | None:
    return _sessions.get(session_id)


def session_exists(session_id: str) -> bool:
    return session_id in _sessions