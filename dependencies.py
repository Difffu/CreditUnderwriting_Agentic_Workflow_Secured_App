from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import SessionLocal
from .utils.security import verify_token
from .logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please log in to access",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception
    
    payload = verify_token(token)
    if not payload:
        logger.warning("Invalid token provided")
        raise credentials_exception
    
    # Normally we'd fetch user from DB, but we'll return email for simplicity
    return payload.get("sub")