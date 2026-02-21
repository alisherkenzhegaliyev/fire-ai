# SQLAlchemy ORM model: tickets table
# Columns (from CSV + NLP enrichment + assignment):
#   id (UUID PK), session_id (str, indexed), customer_guid, gender, date_of_birth,
#   segment (Mass/VIP/Priority), description, attachments,
#   country, region, city, street, building_number,
#   latitude (Float nullable), longitude (Float nullable),
#   request_type, sentiment, priority_score (Int 1-10), language (KZ/ENG/RU), summary,
#   assigned_manager_id (FK → managers.id nullable),
#   assigned_office_id (FK → business_units.id nullable),
#   created_at (DateTime default now)
