import boto3
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image, ImageOps
import io

# --- S3 Configuration ---
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')
s3_client = boto3.client("s3", region_name=S3_REGION)
RESPONSIVE_SIZES = { "small": (480, 480), "medium": (800, 800), "large": (1200, 1200) }

def upload_image(file_storage, folder='general', create_responsive_versions=False):
    """
    MODIFIED: Uploads a file to an S3 bucket and returns the S3 KEY or a dictionary of S3 KEYS.
    """
    original_filename = secure_filename(file_storage.filename)
    unique_prefix = f"{uuid.uuid4().hex[:8]}"

    try:
        file_storage.seek(0)
        img = Image.open(file_storage)
        img = ImageOps.exif_transpose(img)
        img_format = img.format or 'JPEG'
    except Exception as e:
        print(f"Error processing image orientation: {e}")
        return None

    # --- Simple Upload (Non-responsive) ---
    if not create_responsive_versions:
        s3_key = f"{folder}/{unique_prefix}-{original_filename}"
        try:
            in_mem_file = io.BytesIO()
            img.save(in_mem_file, format=img_format)
            in_mem_file.seek(0)
            s3_client.upload_fileobj(in_mem_file, S3_BUCKET, s3_key, ExtraArgs={"ContentType": file_storage.content_type})
            return s3_key # RETURN THE KEY
        except Exception as e:
            print(f"Error during single S3 upload: {e}")
            return None

    # --- Responsive Images Logic ---
    keys = {} # Store keys instead of URLs
    try:
        # Upload responsive versions
        for name, size in RESPONSIVE_SIZES.items():
            img_copy = img.copy()
            img_copy.thumbnail(size)
            in_mem_file = io.BytesIO()
            img_copy.save(in_mem_file, format=img_format)
            in_mem_file.seek(0)
            s3_key = f"{folder}/{unique_prefix}-{name}-{original_filename}"
            s3_client.upload_fileobj(in_mem_file, S3_BUCKET, s3_key, ExtraArgs={"ContentType": file_storage.content_type})
            keys[name] = s3_key # STORE THE KEY

        # Upload the original, full-size image
        in_mem_original = io.BytesIO()
        img.save(in_mem_original, format=img_format)
        in_mem_original.seek(0)
        s3_key_original = f"{folder}/{unique_prefix}-original-{original_filename}"
        s3_client.upload_fileobj(in_mem_original, S3_BUCKET, s3_key_original, ExtraArgs={"ContentType": file_storage.content_type})
        keys['original'] = s3_key_original # STORE THE KEY

        return keys # RETURN DICTIONARY OF KEYS
    except Exception as e:
        print(f"Error during responsive S3 upload: {e}")
        return None

def generate_presigned_url(s3_key, expiration=3600):
    """
    NEW: Generate a pre-signed URL to securely access a private S3 object.
    """
    if not s3_key:
        return None
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration  # URL expires in 1 hour
        )
        return response
    except Exception as e:
        print(f"Error generating presigned URL for key {s3_key}: {e}")
        return None