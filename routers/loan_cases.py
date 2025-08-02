from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.schemas import LoanCaseCreate, LoanCaseResponse, LoanCaseUpdate
from ..database.crud import (
    create_loan_case,
    get_loan_case,
    get_user_loan_cases,
    update_loan_case,
    delete_loan_case
)
from ..utils.dependencies import get_current_user
from ..database.crud import get_user_by_email
from ..utils.logger import logger
 
router = APIRouter(tags=["Loan Cases"])

@router.post("/loan-cases/", response_model=LoanCaseResponse, status_code=status.HTTP_201_CREATED)
def create_new_loan_case(
    loan_case: LoanCaseCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_user)
    if not user:
        logger.error(f"User not found during loan case creation: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return create_loan_case(db, loan_case, user.id)

@router.get("/loan-cases/", response_model=list[LoanCaseResponse])
def read_user_loan_cases(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_user)
    if not user:
        logger.error(f"User not found during loan case retrieval: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return get_user_loan_cases(db, user.id)

@router.get("/loan-cases/{case_id}", response_model=LoanCaseResponse)
def read_loan_case(
    case_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    loan_case = get_loan_case(db, case_id)
    if not loan_case:
        logger.warning(f"Loan case not found: {case_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan case not found"
        )
    
    # Verify ownership
    user = get_user_by_email(db, current_user)
    if loan_case.underwriter_id != user.id:
        logger.warning(f"Unauthorized access to loan case {case_id} by user {current_user}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this loan case"
        )
    
    return loan_case

# Change from PUT to PATCH and use LoanCaseUpdate schema
@router.patch("/loan-cases/{case_id}", response_model=LoanCaseResponse)
def update_existing_loan_case(
    case_id: int,
    loan_case: LoanCaseUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    db_loan_case = get_loan_case(db, case_id)
    if not db_loan_case:
        logger.warning(f"Loan case not found during update: {case_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan case not found"
        )
    
    user = get_user_by_email(db, current_user)
    if db_loan_case.underwriter_id != user.id:
        logger.warning(f"Unauthorized update attempt on loan case {case_id} by user {current_user}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this loan case"
        )
    
    return update_loan_case(db, case_id, loan_case)

@router.delete("/loan-cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_loan_case(
    case_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    db_loan_case = get_loan_case(db, case_id)
    if not db_loan_case:
        logger.warning(f"Loan case not found during deletion: {case_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan case not found"
        )
    
    user = get_user_by_email(db, current_user)
    if db_loan_case.underwriter_id != user.id:
        logger.warning(f"Unauthorized deletion attempt on loan case {case_id} by user {current_user}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this loan case"
        )
    
    delete_loan_case(db, case_id)
    return