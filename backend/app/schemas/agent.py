# Pydantic schemas for AI agent API
# Classes:
#   AgentQueryRequest: { question: str, session_id: str }
#   AgentChartPayload: { type: str (bar/pie/line/scatter), title: str, data: list[dict], x_key: str, y_key: str, color_key: str | None }
#   AgentQueryResponse: { answer: str, chart_data: AgentChartPayload | None }
