import boto3
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image, ImageOps # Import ImageOps
import io

# ... (S3 configuration remains the same) ...
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')
s3_client = boto3.client("s3", region_name=S3_REGION)
RESPONSIVE_SIZES = { "small": (480, 480), "medium": (800, 800), "large": (1200, 1200) }

def upload_image(file_storage, folder='general', create_responsive_versions=False):
    """
    Uploads a file to an S3 bucket, auto-correcting for EXIF orientation.
    If specified, it creates and uploads multiple responsive versions.
    """
    original_filename = secure_filename(file_storage.filename)
    unique_prefix = f"{uuid.uuid4().hex[:8]}"

    try:
        # --- NEW: Read the image and fix orientation ---
        # Read the file into memory and open with Pillow
        file_storage.seek(0)
        img = Image.open(file_storage)

        # Use ImageOps.exif_transpose to apply the EXIF orientation tag
        img = ImageOps.exif_transpose(img)

        # Determine the image format, defaulting to JPEG
        img_format = img.format or 'JPEG'

    except Exception as e:
        print(f"Error processing image orientation: {e}")
        return None # Stop if the image can't be opened

    # --- Simple Upload (for non-responsive images) ---
    if not create_responsive_versions:
        s3_key = f"{folder}/{unique_prefix}-{original_filename}"
        try:
            # Save the corrected image to an in-memory file for upload
            in_mem_file = io.BytesIO()
            img.save(in_mem_file, format=img_format)
            in_mem_file.seek(0)

            s3_client.upload_fileobj(in_mem_file, S3_BUCKET, s3_key, ExtraArgs={"ContentType": file_storage.content_type})
            return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        except Exception as e:
            print(f"Error during single S3 upload: {e}")
            return None

    # --- Responsive Images Logic (now uses the corrected 'img' object) ---
    urls = {}
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
            urls[name] = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

        # Upload the original, full-size (but orientation-corrected) image
        in_mem_original = io.BytesIO()
        img.save(in_mem_original, format=img_format)
        in_mem_original.seek(0)
        s3_key_original = f"{folder}/{unique_prefix}-original-{original_filename}"
        s3_client.upload_fileobj(in_mem_original, S3_BUCKET, s3_key_original, ExtraArgs={"ContentType": file_storage.content_type})
        urls['original'] = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key_original}"

        return urls

    except Exception as e:
        print(f"Error during responsive S3 upload: {e}")
        return None