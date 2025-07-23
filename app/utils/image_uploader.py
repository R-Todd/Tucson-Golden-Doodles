import boto3
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
import io

# Get S3 details from environment variables
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')

# Initialize the S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

# Define standard sizes for responsive images
RESPONSIVE_SIZES = {
    "small": (480, 480),
    "medium": (800, 800),
    "large": (1200, 1200)
}

def upload_image(file_storage, folder='general', create_responsive_versions=False):
    """
    Uploads a file to an S3 bucket. If specified, it creates and uploads
    multiple responsive versions and returns a dictionary of URLs. Otherwise,
    it uploads a single file and returns its URL string.
    """
    original_filename = secure_filename(file_storage.filename)
    unique_prefix = f"{uuid.uuid4().hex[:8]}"

    # If not creating responsive versions, perform a simple upload
    if not create_responsive_versions:
        s3_key = f"{folder}/{unique_prefix}-{original_filename}"
        try:
            s3_client.upload_fileobj(
                file_storage,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": file_storage.content_type}
            )
            return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        except Exception as e:
            print(f"Error during single S3 upload: {e}")
            return None

    # --- Logic for responsive images ---
    urls = {}
    try:
        # Read the file into memory for processing
        file_storage.seek(0)
        img = Image.open(file_storage)
        img_format = img.format or 'JPEG'  # Default to JPEG if format is not detectable

        for name, size in RESPONSIVE_SIZES.items():
            # Create a copy to resize
            img_copy = img.copy()
            img_copy.thumbnail(size)

            # Prepare the file for upload
            in_mem_file = io.BytesIO()
            img_copy.save(in_mem_file, format=img_format)
            in_mem_file.seek(0)

            # Define S3 key and upload
            s3_key = f"{folder}/{unique_prefix}-{name}-{original_filename}"
            s3_client.upload_fileobj(
                in_mem_file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": file_storage.content_type}
            )
            urls[name] = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

        # Also save the original full-size image
        file_storage.seek(0)
        s3_key_original = f"{folder}/{unique_prefix}-original-{original_filename}"
        s3_client.upload_fileobj(
            file_storage,
            S3_BUCKET,
            s3_key_original,
            ExtraArgs={"ContentType": file_storage.content_type}
        )
        urls['original'] = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key_original}"

        return urls

    except Exception as e:
        print(f"Error during responsive S3 upload: {e}")
        return None