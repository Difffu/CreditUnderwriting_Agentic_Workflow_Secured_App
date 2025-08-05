from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from .database import Base

class CreditUnderwriter(Base):
    __tablename__ = "credit_underwriters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    security_question = Column(String, nullable=False)
    security_answer = Column(String, nullable=False)
    loan_cases = Column(ARRAY(Integer), default=[])

class LoanCase(Base):
    __tablename__ = "loan_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False)
    loan_amount = Column(Integer, nullable=False)
    loan_type = Column(String, nullable=False)
    loan_tenure = Column(Integer, nullable=False)
    underwriter_id = Column(Integer, ForeignKey("credit_underwriters.id"))