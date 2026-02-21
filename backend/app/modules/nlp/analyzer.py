# NLP Analyzer Module
# Responsibilities:
#   - analyze_ticket(description: str, segment: str) -> TicketNLPResult
#   - Makes a single LLM API call (OpenAI) per ticket using a structured prompt
#   - Extracts and returns:
#       request_type: one of [Complaint, DataChange, Consultation, Claim, AppMalfunction, FraudulentActivity, Spam]
#       sentiment: one of [Positive, Neutral, Negative]
#       priority_score: int 1-10 (urgency rating)
#       language: one of [KZ, ENG, RU] — defaults to RU if undetectable
#       summary: str — 1-2 sentence summary + recommended next action for manager
#   - Use structured output / JSON mode to ensure parseable response
#   - Handle API errors gracefully with default fallback values
