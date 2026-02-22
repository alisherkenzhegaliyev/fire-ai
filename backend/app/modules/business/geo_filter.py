"""Geographic filter — haversine nearest-office routing + 50/50 distributor for unmapped tickets."""
import math

_R = 6371.0  # Earth radius km

_ASTANA_TOKENS = {"астана", "astana", "нур-султан", "nur-sultan", "нурсултан"}
_ALMATY_TOKENS = {"алматы", "almaty", "алма-ата"}
_KZ_COUNTRIES = {"казахстан", "kazakhstan", "kz", "қазақстан"}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    )
    return _R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_foreign_country(ticket: dict) -> bool:
    """Return True if the ticket's country is not Kazakhstan."""
    country = (ticket.get("country") or "").strip().lower()
    if not country:
        return False
    return country not in _KZ_COUNTRIES


def resolve_office_by_distance(ticket: dict, offices: dict) -> str | None:
    """Return the nearest office name for a geocoded ticket, or None if no coords."""
    lat = ticket.get("latitude")
    lon = ticket.get("longitude")
    if lat is None or lon is None:
        return None

    active = [
        o for o in offices.values()
        if o.get("latitude") is not None and o.get("longitude") is not None
    ]
    if not active:
        return None

    nearest = min(active, key=lambda o: haversine_km(lat, lon, o["latitude"], o["longitude"]))
    return nearest["office"]


def sorted_offices_by_distance(base_office_id: str, offices: dict) -> list[str]:
    """Return other office names sorted ascending by distance from base_office_id."""
    base = offices.get(base_office_id)
    if not base or base.get("latitude") is None:
        return []

    distances: list[tuple[float, str]] = []
    for o in offices.values():
        if o["office"] == base_office_id or o.get("latitude") is None:
            continue
        d = haversine_km(base["latitude"], base["longitude"], o["latitude"], o["longitude"])
        distances.append((d, o["office"]))

    distances.sort()
    return [oid for _, oid in distances]


class FiftyFiftyDistributor:
    """
    Strict 50/50 alternation between the Astana and Almaty offices.
    Used for unmapped tickets (no geocoords) and foreign-country tickets.
    """

    def __init__(self):
        self._next = 0  # 0 = Astana, 1 = Almaty

    def get_next_office(self, offices: dict) -> str | None:
        astana = next(
            (o["office"] for o in offices.values()
             if any(t in (o.get("office") or "").lower() for t in _ASTANA_TOKENS)),
            None,
        )
        almaty = next(
            (o["office"] for o in offices.values()
             if any(t in (o.get("office") or "").lower() for t in _ALMATY_TOKENS)),
            None,
        )
        choices = [x for x in [astana, almaty] if x]
        if not choices:
            return None
        chosen = choices[self._next % len(choices)]
        self._next += 1
        return chosen
