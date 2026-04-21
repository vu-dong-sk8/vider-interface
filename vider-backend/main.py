from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
import datetime

from .database import Base, engine, get_db
from .models import User, ChatMessage
from .ai_service import llm

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VIDER Backend")


class ChatRequest(BaseModel):
    username: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    # find or create user
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        user = User(username=req.username)
        db.add(user)
        db.commit()
        db.refresh(user)

    # save user message
    user_msg = ChatMessage(user_id=user.id, role="user", content=req.message, timestamp=datetime.datetime.utcnow())
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # build chat history from recent messages (simple retrieval)
    msgs = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).order_by(ChatMessage.timestamp.asc()).all()
    chat_history = []
    for m in msgs:
        chat_history.append({"role": m.role, "content": m.content})

    # generate response
    try:
        reply_text = llm.generate_response(chat_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # save assistant message
    assistant_msg = ChatMessage(user_id=user.id, role="assistant", content=reply_text, timestamp=datetime.datetime.utcnow())
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(reply=reply_text)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
