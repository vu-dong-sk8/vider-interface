"""
VIDER Backend — FastAPI server.

Endpoints
---------
POST /chat          Send a message, receive an AI-generated reply.
GET  /health        Health-check (useful for deployment probes).
GET  /chat/history  Retrieve chat history for a user.
"""

import datetime
import logging
import os

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, ChatMessage
from ai_service import get_llm

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("vider")

# ---------------------------------------------------------------------------
# Create tables (safe to call multiple times)
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="VIDER Backend",
    description="Local LLM chat API with PostgreSQL/SQLite persistence.",
    version="1.0.0",
)

# CORS — allow the frontend (any origin for dev, restrict in production)
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    username: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    message_id: int | None = None


class HistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Simple health check for deployment probes."""
    return {"status": "ok", "service": "vider-backend"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """Process a user message and return an AI-generated reply.

    Flow:
    1. Find or create the user.
    2. Save the user message to the database.
    3. Build chat history and call the LLM.
    4. Save the assistant reply to the database.
    5. Return the reply.
    """
    # 1. Find or create user
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        user = User(username=req.username)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Save user message
    user_msg = ChatMessage(
        user_id=user.id,
        role="user",
        content=req.message,
        timestamp=datetime.datetime.utcnow(),
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 3. Build chat history (last 20 messages to keep context manageable)
    recent_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.timestamp.asc())
        .limit(20)
        .all()
    )
    chat_history = [{"role": m.role, "content": m.content} for m in recent_msgs]

    # 4. Generate response
    try:
        llm = get_llm()
        reply_text = llm.generate_response(chat_history)
    except Exception as exc:
        logger.exception("LLM generation failed")
        raise HTTPException(status_code=500, detail=f"AI error: {exc}") from exc

    # 5. Save assistant message
    assistant_msg = ChatMessage(
        user_id=user.id,
        role="assistant",
        content=reply_text,
        timestamp=datetime.datetime.utcnow(),
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(reply=reply_text, message_id=assistant_msg.id)


@app.get("/chat/history", response_model=list[HistoryMessage])
def chat_history(
    username: str = Query(..., description="Username to fetch history for"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return the chat history for a given user (newest first)."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return []

    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        HistoryMessage(
            id=m.id,
            role=m.role,
            content=m.content,
            timestamp=m.timestamp.isoformat() if m.timestamp else "",
        )
        for m in reversed(msgs)  # chronological order
    ]


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
