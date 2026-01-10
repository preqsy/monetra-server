import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from services.kafka_producer import producer

from core.externals.firebase.firebase_init import init_firebase


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Firebase on FastAPI startup
@app.on_event("startup")
def on_startup():
    init_firebase()


@app.on_event("shutdown")
def on_shutdown():
    producer.flush()


app.include_router(router)
