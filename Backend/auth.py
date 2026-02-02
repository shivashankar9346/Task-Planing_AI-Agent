from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import UserTable, get_db
from .utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(user: AuthRequest, db: Session = Depends(get_db)):
    existing_user = db.query(UserTable).filter(
        UserTable.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = hash_password(user.password)
    new_user = UserTable(username=user.username, hashed_password=hashed)

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


@router.post("/login")
def login(user: AuthRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserTable).filter(
        UserTable.username == user.username
    ).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Account not found or invalid credentials"
        )

    token = create_access_token(db_user.username)
    return {"access_token": token, "token_type": "bearer"}
