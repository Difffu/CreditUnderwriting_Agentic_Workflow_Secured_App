import boto3
import os
from fastapi import HTTPException
from ..utils.logger import logger

class S3Uploader:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket = os.getenv('S3_BUCKET_NAME')

    def upload_file(self, file_path: str, s3_key: str):
        try:
            self.client.upload_file(
                file_path,
                self.bucket,
                s3_key
            )
            logger.info(f"Successfully uploaded {file_path} to S3 as {s3_key}")
            return f"s3://{self.bucket}/{s3_key}"
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"S3 upload failed: {str(e)}"
            )

s3_uploader = S3Uploader()