import time

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel
from src.features.chat.service import get_ai_response


app = FastAPI(
    title="Turing Test API",
    description="API لخدمة اختبار تورنغ المباشر بين المُحكّم والأطراف المخفية.",
    version="1.0.0"
)

chat_history = []
round_started_at: float | None = None
ROUND_DURATION_SECONDS = 5 * 60
judge_current_selection: str | None = None

class Message(BaseModel):
    role: str
    sender: str
    content: str
    judge_gender: str | None = None


@app.post("/api/chat/round/start")
def start_round():
    """start the five-minute round once the judge enters the room"""

    global round_started_at

    if round_started_at is None:
        round_started_at = time.time()

    return {
        "started_at": round_started_at,
        "duration_seconds": ROUND_DURATION_SECONDS,
    }


@app.get("/api/chat/round/state")
def get_round_state():
    """return the shared round timer state"""

    if round_started_at is None:
        return {
            "started": False,
            "started_at": None,
            "duration_seconds": ROUND_DURATION_SECONDS,
            "remaining_seconds": ROUND_DURATION_SECONDS,
            "expired": False,
        }

    elapsed_seconds = int(time.time() - round_started_at)
    remaining_seconds = max(0, int(ROUND_DURATION_SECONDS) - elapsed_seconds)

    return {
        "started": True,
        "started_at": round_started_at,
        "duration_seconds": ROUND_DURATION_SECONDS,
        "remaining_seconds": remaining_seconds,
        "expired": remaining_seconds == 0,
    }

@app.get("/api/chat/history")
def get_chat_history():
    """return the entire chat history for the judge and guest view"""

    return chat_history

@app.post("/api/chat/judge_ask")
def judge_ask(message: Message, background_tasks: BackgroundTasks):
    """endpoint to receive judge's question and broadcast it to participants"""
    
    chat_history.append(message.model_dump())

    background_tasks.add_task(genai_reply, message.content, list(chat_history), message.judge_gender)

    return { "status": "success" }


def genai_reply(question: str, history: list[dict], judge_gender: str | None):
    ai_text = get_ai_response(question, history=history, judge_gender=judge_gender)    

    chat_history.append({
        "role": "participant",
        "sender": "الطرف (ب)", 
        "content": ai_text
    })

@app.delete("/api/chat/reset")
def reset_chat():
    """endpoint to clear the chat history (for testing purposes)"""

    global round_started_at, judge_current_selection

    chat_history.clear()
    round_started_at = None
    judge_current_selection = None
    return { "status": "cleared" }

class VerdictSelection(BaseModel):
    selection: str | None

@app.post("/api/chat/verdict/selection")
def set_verdict_selection(verdict: VerdictSelection):
    """Update the judge's current selection (live tracking)"""
    global judge_current_selection
    judge_current_selection = verdict.selection
    return {"status": "success"}

@app.get("/api/chat/verdict/selection")
def get_verdict_selection():
    """Get the judge's current selection"""
    return {"selection": judge_current_selection}

@app.post("/api/chat/human_reply")
def human_reply(message: Message):
    """endpoint to receive the hidden human's reply and broadcast it"""
    
    chat_history.append(message.model_dump())
    
    return { "status": "success" }