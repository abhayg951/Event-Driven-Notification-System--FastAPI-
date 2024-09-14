# This is the Producer that will send the notifications through the message Broker
from fastapi import FastAPI
from .connection import get_db_connection
from contextlib import asynccontextmanager
from .user_routes import router

db = get_db_connection()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to database...")

    yield # the application runs during this yield

    print("Closing database connection...")

app = FastAPI(lifespan=lifespan)

app.include_router(router)