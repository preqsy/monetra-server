import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monetra_server.api import router
from monetra_server.core.redis import close_redis, init_redis_client
from monetra_server.services.kafka_producer import producer
from monetra_server.core import settings
from monetra_server.core.externals.firebase.firebase_init import init_firebase

load_dotenv()

logfire.configure(service_name="monetraserver", environment=settings.ENVIRONMENT)
logfire.info(f"Starting Monetra Server in {settings.ENVIRONMENT} environment...")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_firebase()
    init_redis_client()
    yield
    producer.flush()
    close_redis()


app = FastAPI(lifespan=lifespan)
logfire.instrument_fastapi(app)

# origins = ["*"]

origins = [
    "https://www.monetrify.online",
    "https://monetrify.online",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
