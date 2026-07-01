
from pathlib import Path
import secrets
import shutil

import boto3
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ApiException


s3_client = boto3.client(
    "s3",
    aws_access_key_id= settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name="eu-north-1"
)


async def upload_to_s3(file: UploadFile, folder:str) -> str:
    print("inside upload_to_s3")
    try:
        unique_name = f"{secrets.token_hex(2)}_{file.filename}"
        s3_file_name = f"{folder}/{unique_name}"

        s3_client.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            s3_file_name,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        return f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_file_name}"
    
    except Exception as e:
        raise ApiException(f"s3 uplaod failed: {str(e)}", 500)




async def upload_file(file: UploadFile, upload_dir: Path) -> str:

    
    print("inside upload_file in upload.py")

    upload_dir.mkdir(parents=True, exist_ok=True)


    print("passed mkdir helding tp generate unique filename")

    unique_name = f"{secrets.token_hex(2)}_{file.filename}"
    file_path = upload_dir / unique_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/{upload_dir}/{unique_name}"