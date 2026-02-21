# Application configuration using pydantic-settings
# Responsibilities:
#   - Load environment variables from .env file
#   - Settings class fields:
#       - DATABASE_URL: str
#       - OPENAI_API_KEY: str
#       - GEOCODING_API_KEY: str (optional, for external geocoding service)
#       - FRONTEND_ORIGIN: str (for CORS)
#   - Expose a singleton `settings` instance imported by other modules
