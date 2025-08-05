from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.schemas import CreditUnderwriterCreate, Token, Login, ForgotPassword
from ..database.crud import create_user, get_user_by_email, update_user_password
from ..auth.security import verify_password, create_access_token
from ..auth.dependencies import get_current_user
from ..utils.logger import logger

router = APIRouter(tags=["Authentication"]) 

@router.post("/signup", response_model=Token)
def signup(user: CreditUnderwriterCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        logger.warning(f"Signup attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = create_user(db, user)
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.username)
    if not user or not verify_password(login_data.password, user.password):
        logger.warning(f"Failed login attempt for email: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/forgot-password")
def forgot_password(forgot_data: ForgotPassword, db: Session = Depends(get_db)):
    user = get_user_by_email(db, forgot_data.email)
    if not user:
        logger.warning(f"Password reset attempt for non-existent email: {forgot_data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if forgot_data.security_answer != user.security_answer:
        logger.warning(f"Invalid security answer for email: {forgot_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security answer"
        )
    
    update_user_password(db, forgot_data.email, forgot_data.new_password)
    return {"message": "Password updated successfully"}

@router.get("/me")
def get_current_user_endpoint(current_user: str = Depends(get_current_user)):
    return {"email": current_user}