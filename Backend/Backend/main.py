import os
import bcrypt
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_planner_key_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

# --- DIRECT BCRYPT SECURITY (Fixes Passlib Bugs) ---
def hash_password(password: str) -> str:
    # Truncate to 72 bytes as per bcrypt limits
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(pw_bytes, hashed_password.encode('utf-8'))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- APP INITIALIZATION ---
app = FastAPI(title="AI Agent Planner Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=GROQ_API_KEY)

# --- DATA MODELS ---
class AuthRequest(BaseModel):
    username: str
    password: str

class UserInput(BaseModel):
    message: str
    conversation_id: str

# --- AUTHENTICATION ROUTES ---

@app.post("/register")
def register(user: AuthRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserTable).filter(UserTable.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Use our direct bcrypt hashing
    hashed = hash_password(user.password)
    
    new_user = UserTable(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: AuthRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserTable).filter(UserTable.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail="Account not found or invalid credentials. Please register first."
        )
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": db_user.username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}

# --- AI CHAT LOGIC ---
conversations: Dict[str, List[Dict[str, str]]] = {}

# main.py - Update this section
@app.post("/chat/")
async def chat(input_data: UserInput):
    cid = input_data.conversation_id
    
    if cid not in conversations:
        conversations[cid] = [
            {
                "role": "system", 
                "content": (
                    "You are a Goal Planner AI. "
                    "CRITICAL: Always provide your response in a clean, point-wise format. "
                    "Use bullet points (*) or numbered lists. "
                    "Avoid long paragraphs. Keep each point concise."
                )
            }
        ]
    
    # ... rest of your code stays the same
    
    conversations[cid].append({"role": "user", "content": input_data.message})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversations[cid],
            temperature=0.7,
        )
        ai_msg = completion.choices[0].message.content
        conversations[cid].append({"role": "assistant", "content": ai_msg})
        return {"response": ai_msg}
    except Exception as e:
        print(f"Groq API Error: {e}")
        raise HTTPException(status_code=500, detail="AI response failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)