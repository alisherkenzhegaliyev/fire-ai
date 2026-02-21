# GET /api/managers?session_id=xxx
# Responsibilities:
#   - Query all Manager records for the given session_id
#   - Include current workload count (number of tickets assigned in this session)
#   - Return list of ManagerResponse (all manager fields + workload)
