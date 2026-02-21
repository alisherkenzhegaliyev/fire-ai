# Geographic Filter Module
# Responsibilities:
#   - geocode_address(country, region, city, street, building) -> (lat, lon) | None
#       Uses geocoding API (e.g. Nominatim via geopy) to convert text address to coordinates
#   - find_nearest_office(lat, lon, offices: list[BusinessUnit]) -> BusinessUnit
#       Uses haversine formula to compute great-circle distance between customer and each office
#       Returns the closest office
#   - handle_unknown_address(offices: list[BusinessUnit], counter: int) -> BusinessUnit
#       For customers with unknown address or abroad: alternate 50/50 between Astana and Almaty offices
#       counter tracks the round-robin split between the two
