# Pydantic schemas for analytics API
# Classes:
#   DistributionBucket: { label: str, count: int, percentage: float }
#   AnalyticsResponse: {
#       total_tickets, total_managers, assigned_count, unassigned_count,
#       by_segment, by_request_type, by_sentiment, by_language, by_office: list[DistributionBucket],
#       avg_priority_score: float
#   }
