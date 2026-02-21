import os
from sqlalchemy import create_engine, text
from config import get_settings

# Create the engine to connect to PostgreSQL (without specifying the database)
engine = create_engine(get_settings().DATABASE_URL,
                       isolation_level="AUTOCOMMIT", pool_pre_ping=True)

# Function to create the database if it does not exist


def create_database():
    # Connect to PostgreSQL server and create the database
    try:
        with engine.connect() as connection:
            if os.getenv("ENV") == "test":
                connection.execute(
                    text(f"DROP DATABASE {get_settings().DATABASE_NAME}"))
    except Exception as e:
        print(f"Error: {e}")

    try:
        # Connect to PostgreSQL server and create the database
        with engine.connect() as connection:
            connection.execute(
                text(f"CREATE DATABASE {get_settings().DATABASE_NAME}"))
            print(
                f"Database '{get_settings().DATABASE_NAME}' created successfully.")
    except Exception as e:
        print(f"Error: {e}")
        # If the database already exists, this exception will be triggered.


# Main execution to create the database and tables
if __name__ == "__main__":
    # Create the database if it does not exist
    create_database()
