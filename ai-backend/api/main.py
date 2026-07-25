"""
Suraksha API — entry point.

Run locally with:
    uvicorn api.main:app --reload --port 8000

Then check http://127.0.0.1:8000/docs for interactive Swagger UI, which
Person B can also use to see the exact request/response shapes.
"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db.logging import init_db
from api.routes import analyze_call, analyze_message, guardian_alert

load_dotenv()
init_db()  # creates the flagged_messages table if it doesn't exist yet

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


@app.get("/health")
def health_check():
    return {"status": "ok"}
