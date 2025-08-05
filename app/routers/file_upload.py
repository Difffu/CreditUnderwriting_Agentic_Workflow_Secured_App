import os
import zipfile
import tempfile
import uuid
import filetype  # NEW - cross-platform alternative
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..utils.s3_utils import s3_uploader
from ..database.schemas import ZipUploadResponse
from ..auth.dependencies import get_current_user
from ..utils.logger import logger

router = APIRouter(tags=["File Upload"])

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
    'text/plain'
}

def validate_file_type(file_path: str):
    """Validate file type using filetype library"""
    try:
        kind = filetype.guess(file_path)
        if not kind or kind.mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {getattr(kind, 'mime', 'unknown')} not allowed"
            )
        return kind.mime
    except Exception as e:
        logger.error(f"File type validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )

@router.post("/upload-zip", response_model=ZipUploadResponse)
async def upload_zip(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    try:
        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = os.path.join(temp_dir, file.filename)
            
            # Save uploaded zip file
            with open(temp_zip_path, "wb") as f:
                f.write(await file.read())
            
            # Verify it's a zip file
            if not zipfile.is_zipfile(temp_zip_path):
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is not a valid ZIP archive"
                )
            
            extracted_files = []
            s3_paths = []
            
            # Extract and process files
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if zip_info.is_dir():
                        continue
                    
                    extracted_path = os.path.join(temp_dir, zip_info.filename)
                    zip_ref.extract(zip_info, temp_dir)
                    
                    # Validate file type
                    try:
                        validate_file_type(extracted_path)
                    except HTTPException as e:
                        logger.warning(f"Skipping invalid file {zip_info.filename}: {e.detail}")
                        continue
                    
                    # Generate unique S3 key
                    file_ext = os.path.splitext(zip_info.filename)[1]
                    s3_key = f"{uuid.uuid4()}{file_ext}"
                    
                    # Upload to S3
                    s3_path = s3_uploader.upload_file(extracted_path, s3_key)
                    
                    extracted_files.append(zip_info.filename)
                    s3_paths.append(s3_path)
            
            if not extracted_files:
                raise HTTPException(
                    status_code=400,
                    detail="No valid files found in ZIP archive"
                )
            
            return ZipUploadResponse(
                original_filename=file.filename,
                extracted_files=extracted_files,
                s3_paths=s3_paths,
                message=f"Successfully processed {len(extracted_files)} files"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing ZIP file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing ZIP file: {str(e)}"
        )