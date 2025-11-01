from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router

from core.externals.firebase.firebase_init import init_firebase


app = FastAPI()

origins = [
    # "http://localhost:5173",  # if you're using Vite
    "http://localhost:8080",  # if another dev port
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


# Fallback middleware to ensure Access-Control-Allow-Origin is present even when
# unexpected exceptions occur (some exception paths may not include CORS headers).
@app.middleware("http")
async def ensure_cors_header(request, call_next):
    from fastapi.responses import PlainTextResponse

    try:
        response = await call_next(request)
    except Exception:
        # Return a minimal 500 response with CORS headers so the browser doesn't
        # block the response due to missing CORS headers.
        msg = "Internal Server Error"
        resp = PlainTextResponse(msg, status_code=500)
        try:
            # Use configured origins where possible
            resp.headers["Access-Control-Allow-Origin"] = (
                ",".join(origins) if origins else "*"
            )
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "*"
        except Exception:
            pass
        return resp

    # If response doesn't already have CORS headers, add them
    if "access-control-allow-origin" not in {
        k.lower() for k in response.headers.keys()
    }:
        try:
            response.headers["Access-Control-Allow-Origin"] = (
                ",".join(origins) if origins else "*"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
        except Exception:
            pass

    return response
