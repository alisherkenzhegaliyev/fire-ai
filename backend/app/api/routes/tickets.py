# GET /api/tickets?session_id=xxx
# Responsibilities:
#   - Query all Ticket records for the given session_id
#   - Join with Assignment records to include assigned manager and office info
#   - Return list of TicketResponse (all CSV fields + NLP enrichment + assignment chain)
