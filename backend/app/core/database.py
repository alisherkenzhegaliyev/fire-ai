# SQLAlchemy database setup
# Responsibilities:
#   - Create SQLAlchemy engine from settings.DATABASE_URL
#   - Create SessionLocal factory (autocommit=False, autoflush=False)
#   - Declare Base = declarative_base() used by all ORM models
#   - Expose create_tables() helper that calls Base.metadata.create_all(engine)
