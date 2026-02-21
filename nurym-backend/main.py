import os
from fastapi import FastAPI
from database import Base, engine
from controllers.auth_controller import auth_controller
from create_db import create_database
from middlewares import cors_middleware
from middlewares import static_middleware

app = FastAPI()

if not os.getenv("ENV"):
    os.environ["ENV"] = "dev"

cors_middleware.add(app)
static_middleware.add(app)

create_database()
# Initialize the database
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_controller.router, prefix="/auth", tags=["auth"])
