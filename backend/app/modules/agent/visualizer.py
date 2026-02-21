# AI Agent Visualizer Module (Star Task)
# Responsibilities:
#   - handle_query(question: str, session_id: str, db: Session) -> AgentQueryResponse
#       1. Send user question to LLM with context about available data fields
#          (ticket segments, request types, sentiments, offices, managers, cities, etc.)
#       2. LLM decides which aggregation to perform and returns structured instructions:
#          { sql_or_aggregation: str, chart_type: str, x_key: str, y_key: str, title: str }
#       3. Execute the aggregation against DB (scoped to session_id)
#       4. Format results as list[dict] for chart rendering
#       5. Generate a natural language answer summarizing the findings
#       6. Return AgentQueryResponse { answer, chart_data: AgentChartPayload | None }
#   - Supports chart types: bar, pie, line, scatter
#   - Example queries:
#       "Show distribution of request types by city"
#       "Which managers have the highest workload?"
#       "Show sentiment breakdown for VIP segment"
