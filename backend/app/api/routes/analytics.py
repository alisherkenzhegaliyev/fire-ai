# GET /api/analytics?session_id=xxx
# Responsibilities:
#   - Aggregate ticket data for the given session into summary statistics:
#       - totalTickets, totalManagers, assignedCount, unassignedCount
#       - bySegment, byRequestType, bySentiment, byLanguage, byOffice (DistributionBucket lists)
#       - avgPriorityScore
#   - Return AnalyticsResponse
