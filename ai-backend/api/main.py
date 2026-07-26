"""
Suraksha API — entry point.

Run locally with:
    uvicorn api.main:app --reload --port 8000

Then check http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.db.logging import init_db
from api.routes import analyze_call, analyze_message, guardian_alert

load_dotenv()
init_db()  # creates the flagged_messages table if it doesn't exist yet

logger = logging.getLogger("suraksha")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Suraksha API",
    description="Scam detection for first-time digital banking users in rural India.",
    version="0.1.0",
)

# Wide open for hackathon dev; tighten before demo day if time allows.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_message.router)
app.include_router(analyze_call.router)
app.include_router(guardian_alert.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches anything not already handled by a route's own try/except
    (e.g. HTTPException raised deliberately still works normally -- this
    only catches genuinely unexpected crashes). Logs the real error
    server-side for debugging, but never hands the client a raw Python
    traceback -- that can leak file paths and internal details, and
    reads badly if a judge happens to trigger one during a demo.
    """
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong processing this request. Please try again."},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
