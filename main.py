from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router

from core.externals.firebase.firebase_init import init_firebase


app = FastAPI()

origins = [
    # "http://localhost:5173",  # if you're using Vite
    # "http://localhost:8080",  # if another dev port
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # now allowed because origins are specific
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Firebase on FastAPI startup
@app.on_event("startup")
def on_startup():
    init_firebase()


app.include_router(router)
