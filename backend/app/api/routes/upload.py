# POST /api/upload
# Responsibilities:
#   - Accept multipart CSV file upload
#   - Call csv_parser to parse all three CSV tables (tickets, managers, business units) and persist to DB
#   - Trigger nlp/analyzer async pipeline on each ticket (type, sentiment, priority, lang, summary)
#   - After NLP enrichment, trigger business module pipeline:
#       1. geo_filter: geocode address → lat/lon → find nearest office
#       2. competency_filter: filter eligible managers by segment/language/position rules
#       3. assignment: round-robin between two lowest-workload eligible managers
#   - Update DB with all enrichment and assignment results
#   - Return UploadResponse: { session_id, ticket_count, manager_count, status }
