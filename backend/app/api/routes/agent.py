# POST /api/agent/query
# Responsibilities:
#   - Accept AgentQueryRequest: { question: str, session_id: str }
#   - Call modules/agent/visualizer to:
#       1. Use LLM to understand the user's question
#       2. Query DB for relevant data scoped to session_id
#       3. Format data and generate a chart payload (type, title, data, xKey, yKey)
#   - Return AgentQueryResponse: { answer: str, chart_data?: AgentChartPayload }
