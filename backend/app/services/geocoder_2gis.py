"""2GIS Geocoding service — async, with in-memory cache and concurrency control."""
import asyncio
import math
import re
import logging

import httpx

log = logging.getLogger(__name__)

_API_KEY = "e560747c-3197-4618-8643-e01aa778b523"
_BASE_URL = "https://catalog.api.2gis.com/3.0/items/geocode"


def _clean(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    s = str(v).strip()
    return s if s else None


def _norm_city(city: str | None) -> str | None:
    if not city:
        return None
    c = city.strip()
    c = re.sub(r"^г\.\s*", "", c, flags=re.IGNORECASE)
    c = c.split("/")[0].strip()
    c = re.sub(r"\(.*?\)", "", c).strip()
    return c if c else None


def _join(*parts) -> str:
    xs = [str(p).strip() for p in parts if p and str(p).strip()]
    return ", ".join(xs)


class TwoGISProvider:
    def __init__(self, api_key: str = _API_KEY, concurrency: int = 5):
        self.api_key = api_key
        self.sem = asyncio.Semaphore(concurrency)
        self.client = httpx.AsyncClient(timeout=20.0)
        self._cache: dict = {}
        self._city_cache: dict = {}

    async def close(self):
        await self.client.aclose()

    async def _geocode_raw(
        self,
        q: str,
        *,
        city_id: str | None = None,
        location: str | None = None,
        radius: int | None = None,
    ) -> list:
        if not q or not q.strip():
            return []

        key = (q, city_id, location, radius)
        if key in self._cache:
            item = self._cache[key]
            return [item] if item else []

        params: dict = {
            "q": q,
            "key": self.api_key,
            "locale": "ru_KZ",
            "fields": "items.point,items.full_name,items.name,items.id,items.type",
        }
        if city_id:
            params["city_id"] = city_id
        if location:
            params["location"] = location
        if radius is not None:
            params["radius"] = radius

        async with self.sem:
            try:
                r = await self.client.get(_BASE_URL, params=params)
            except Exception as exc:
                log.warning("2GIS request error: %s", exc)
                return []

        if r.status_code in (401, 403, 429):
            log.warning("2GIS returned %d for query: %s", r.status_code, q)
            return []

        try:
            r.raise_for_status()
        except Exception:
            return []

        data = r.json()
        items = (data.get("result") or {}).get("items") or []
        self._cache[key] = items[0] if items else None
        return items

    async def _resolve_city(
        self, city: str, country: str = "Казахстан"
    ) -> tuple[str | None, float | None, float | None]:
        k = (city, country)
        if k in self._city_cache:
            return self._city_cache[k]

        items = await self._geocode_raw(_join(city, country))
        city_id = None
        lat = lon = None

        if items:
            it = items[0]
            cid = str(it.get("id") or "")
            if cid.isdigit():
                city_id = cid
            p = it.get("point") or {}
            lat = p.get("lat")
            lon = p.get("lon")

        out = (
            city_id,
            float(lat) if lat is not None else None,
            float(lon) if lon is not None else None,
        )
        self._city_cache[k] = out
        return out

    async def geocode_address(
        self,
        *,
        country: str | None,
        region: str | None,
        city: str | None,
        street: str | None,
        house: str | None,
    ) -> tuple[float | None, float | None]:
        city_n = _norm_city(_clean(city))
        country_s = _clean(country) or "Казахстан"

        if not city_n:
            return (None, None)

        city_id, c_lat, c_lon = await self._resolve_city(city_n, country=country_s)

        addr_line = " ".join(x for x in [_clean(street), _clean(house)] if x)
        q_full = _join(addr_line, city_n, _clean(region), country_s)
        q_city = _join(city_n, country_s)

        location: str | None = None
        if c_lon is not None and c_lat is not None:
            location = f"{c_lon},{c_lat}"

        if addr_line:
            items = await self._geocode_raw(
                q_full, city_id=city_id, location=location, radius=40000
            )
            if items:
                p = items[0].get("point") or {}
                if p.get("lat") is not None and p.get("lon") is not None:
                    return (float(p["lat"]), float(p["lon"]))

        items = await self._geocode_raw(
            q_city, city_id=city_id, location=location, radius=40000
        )
        if items:
            p = items[0].get("point") or {}
            if p.get("lat") is not None and p.get("lon") is not None:
                return (float(p["lat"]), float(p["lon"]))

        return (c_lat, c_lon)


async def geocode_batch(tickets: list[dict]) -> list[dict]:
    """Geocode all tickets in parallel. Sets 'latitude' and 'longitude' on each dict."""
    provider = TwoGISProvider(concurrency=5)
    try:
        tasks = [
            provider.geocode_address(
                country=t.get("country"),
                region=t.get("region"),
                city=t.get("city"),
                street=t.get("street"),
                house=t.get("building_number"),
            )
            for t in tickets
        ]
        results = await asyncio.gather(*tasks)
        for ticket, (lat, lon) in zip(tickets, results):
            ticket["latitude"] = lat
            ticket["longitude"] = lon
    finally:
        await provider.close()
    return tickets
