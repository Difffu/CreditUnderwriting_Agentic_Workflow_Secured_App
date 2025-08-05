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

# Add this after LoanCaseCreate
class LoanCaseUpdate(BaseModel):
    business_name: Optional[str] = None
    loan_amount: Optional[int] = None
    loan_type: Optional[str] = None
    loan_tenure: Optional[int] = None

class LoanCaseResponse(LoanCaseBase):
    id: int
    underwriter_id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    username: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr
    security_answer: str
    new_password: str = Field(..., min_length=8)


class ZipUploadResponse(BaseModel):
    original_filename: str
    extracted_files: list[str]
    s3_paths: list[str]
    message: str