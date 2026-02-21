# Pydantic schemas for ticket API
# Classes:
#   TicketCreate: fields from CSV row (used internally by csv_parser)
#   TicketNLPUpdate: NLP enrichment fields (request_type, sentiment, priority_score, language, summary, lat, lon)
#   TicketResponse: full response schema (all fields + assigned_manager_name + assigned_office_name)
