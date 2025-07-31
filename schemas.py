from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class CreditUnderwriterBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class CreditUnderwriterCreate(CreditUnderwriterBase):
    password: str = Field(..., min_length=8)
    security_question: str
    security_answer: str

class CreditUnderwriterResponse(CreditUnderwriterBase):
    id: int
    loan_cases: List[int] = []
    
    class Config:
        from_attributes = True

class LoanCaseBase(BaseModel):
    business_name: str
    loan_amount: int
    loan_type: str
    loan_tenure: int

class LoanCaseCreate(LoanCaseBase):
    pass

class LoanCaseResponse(LoanCaseBase):
    id: int
    underwriter_id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr
    security_answer: str
    new_password: str = Field(..., min_length=8)