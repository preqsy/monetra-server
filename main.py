import logging
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from core.redis import close_redis, init_redis_client
from services.kafka_producer import producer
from core import settings
from core.externals.firebase.firebase_init import init_firebase


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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
