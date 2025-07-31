from sqlalchemy.orm import Session
import models, schemas
from utils.security import get_password_hash
from logger import logger

# User operations
def get_user_by_email(db: Session, email: str):
    return db.query(models.CreditUnderwriter).filter(models.CreditUnderwriter.email == email).first()

def create_user(db: Session, user: schemas.CreditUnderwriterCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.CreditUnderwriter(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        security_question=user.security_question,
        security_answer=user.security_answer
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {user.email}")
    return db_user

def update_user_password(db: Session, email: str, new_password: str):
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Password update attempt for non-existent user: {email}")
        return None
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    logger.info(f"Password updated for user: {email}")
    return user

# Loan case operations
def create_loan_case(db: Session, loan_case: schemas.LoanCaseCreate, underwriter_id: int):
    db_loan_case = models.LoanCase(
        **loan_case.dict(),
        underwriter_id=underwriter_id
    )
    db.add(db_loan_case)
    db.commit()
    db.refresh(db_loan_case)
    
    # Add loan case to underwriter's list
    underwriter = db.query(models.CreditUnderwriter).get(underwriter_id)
    if underwriter:
        underwriter.loan_cases = list(set(underwriter.loan_cases + [db_loan_case.id]))
        db.commit()
        db.refresh(underwriter)
    
    logger.info(f"Loan case created: {db_loan_case.id}")
    return db_loan_case

def get_loan_case(db: Session, case_id: int):
    return db.query(models.LoanCase).filter(models.LoanCase.id == case_id).first()

def get_user_loan_cases(db: Session, underwriter_id: int):
    return db.query(models.LoanCase).filter(models.LoanCase.underwriter_id == underwriter_id).all()

def update_loan_case(db: Session, case_id: int, loan_case: schemas.LoanCaseCreate):
    db_loan_case = get_loan_case(db, case_id)
    if not db_loan_case:
        return None
    for key, value in loan_case.dict().items():
        setattr(db_loan_case, key, value)
    db.commit()
    db.refresh(db_loan_case)
    logger.info(f"Loan case updated: {case_id}")
    return db_loan_case

def delete_loan_case(db: Session, case_id: int):
    db_loan_case = get_loan_case(db, case_id)
    if not db_loan_case:
        return False
    
    # Remove from underwriter's list
    underwriter = db.query(models.CreditUnderwriter).get(db_loan_case.underwriter_id)
    if underwriter:
        underwriter.loan_cases = [case for case in underwriter.loan_cases if case != case_id]
        db.commit()
    
    db.delete(db_loan_case)
    db.commit()
    logger.info(f"Loan case deleted: {case_id}")
    return True