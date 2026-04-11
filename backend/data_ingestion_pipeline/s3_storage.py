"""
Upload images to S3 under a folder named after the PDF.
"""

import boto3
from pathlib import Path

S3_BUCKET = "hyp-rag-image-storage"
S3_REGION = "us-west-2"

s3 = boto3.client("s3", region_name=S3_REGION)


def upload_image(local_path: str, pdf_stem: str) -> str:
    """Upload image to S3 under {pdf_stem}/ folder, return public URL."""
    path = Path(local_path)
    if not path.exists():
        return ""

    key = f"{pdf_stem}/{path.name}"
    s3.upload_file(str(path), S3_BUCKET, key, ExtraArgs={"ContentType": "image/jpeg"})

    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
