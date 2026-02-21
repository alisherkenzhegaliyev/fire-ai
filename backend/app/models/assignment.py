# SQLAlchemy ORM model: assignments table (full chain record)
# Columns:
#   id (UUID PK), session_id (str, indexed),
#   ticket_id (FK → tickets.id),
#   manager_id (FK → managers.id nullable),
#   office_id (FK → business_units.id nullable),
#   distance_km (Float): distance from customer to assigned office,
#   assignment_reason (str): human-readable explanation of why this manager was selected,
#   round_robin_index (Int): position in round-robin sequence,
#   created_at (DateTime default now)
# Purpose: supports viewing the full assignment chain Lead → AI Analytics → Assigned Manager
