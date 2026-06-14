import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from src.config.logger import logger

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"
BUCKET_NAME = "kyc-documents"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)


def upload_file_to_s3(file_obj, destination_path: str, content_type: str) -> str:
    try:
        s3_client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=BUCKET_NAME,
            Key=destination_path,
            ExtraArgs={"ContentType": content_type},
        )
        file_url = f"{MINIO_ENDPOINT}/{BUCKET_NAME}/{destination_path}"
        return file_url
    except ClientError as e:
        logger.error("upload_file_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document to storage server.",
        )


def create_presigned_url(file_url: str, expiration_seconds: int = 900) -> str:
    if not file_url:
        return ""

    object_key = file_url.split(f"/{BUCKET_NAME}/")[-1]

    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": object_key},
            ExpiresIn=expiration_seconds,
        )

        return presigned_url.replace("http://minio:9000", "http://localhost:9000")
    except ClientError as e:
        logger.error("create_presigned_url_failed", error=str(e))
        return file_url
