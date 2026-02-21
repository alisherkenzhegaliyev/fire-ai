# Geocoder Service
# Responsibilities:
#   - geocode(country: str, region: str, city: str, street: str, building: str) -> tuple[float, float] | None
#       Combines address fields into a query string
#       Uses geopy (Nominatim) or a configured geocoding API to resolve coordinates
#       Returns (latitude, longitude) or None if address is unresolvable
#   - batch_geocode(addresses: list[dict]) -> list[tuple[float, float] | None]
#       Geocodes a list of address dicts with rate-limit handling (1 req/sec for Nominatim)
#   - Note: cache results to avoid re-geocoding identical addresses within a session
