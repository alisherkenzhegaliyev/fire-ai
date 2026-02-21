# Competency Filter Module
# Responsibilities:
#   - filter_eligible_managers(managers: list[Manager], ticket: Ticket) -> list[Manager]
#       Applies cascade of hard skill rules:
#       1. Office filter: only managers from the selected office (already pre-filtered by geo_filter)
#       2. VIP/Priority segment: manager must have 'VIP' skill
#       3. DataChange request type: manager must have position == 'ChiefSpecialist'
#       4. KZ language: manager must have 'KZ' skill
#       5. ENG language: manager must have 'ENG' skill
#       Rules are cumulative — all applicable rules must pass
#   - Returns filtered list of eligible managers (may be empty if no match)
