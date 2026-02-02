from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from groq import Groq
import os

router = APIRouter(prefix="/chat", tags=["AI Chat"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversations: Dict[str, List[Dict[str, str]]] = {}


class UserInput(BaseModel):
    message: str
    conversation_id: str


@router.post("/")
async def chat(input_data: UserInput):
    cid = input_data.conversation_id

    if cid not in conversations:
        conversations[cid] = [
            {
                "role": "system",
                "content": (
                    "You are a Goal Planner AI. "
                    "Always respond in bullet points or numbered steps. "
                    "Keep answers short and structured."
                )
            }
        ]

    conversations[cid].append(
        {"role": "user", "content": input_data.message}
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversations[cid],
            temperature=0.7,
        )

        ai_msg = completion.choices[0].message.content
        conversations[cid].append(
            {"role": "assistant", "content": ai_msg}
        )

        return {"response": ai_msg}

    except Exception as e:
        print("Groq Error:", e)
        raise HTTPException(status_code=500, detail="AI response failed")
