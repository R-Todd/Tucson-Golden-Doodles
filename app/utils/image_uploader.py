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

RESPONSIVE_SIZES = {
    "small": (480, 480),
    "medium": (800, 800),
    "large": (1200, 1200)
}

# Map Pillow formats to HTTP Content-Types
FORMAT_TO_CONTENT_TYPE = {
    "JPEG": "image/jpeg",
    "JPG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}


def _normalize_for_save(img: Image.Image, fmt: str, background_rgb=(255, 255, 255)) -> Image.Image:
    """
    Ensures the PIL image is compatible with the target format.

    - JPEG does not support alpha, so RGBA/LA/P w/transparency must be flattened onto a background.
    - For JPEG, we also guarantee RGB mode.
    - For PNG, we keep alpha if present.
    """
    fmt = (fmt or "JPEG").upper()

    # Only JPEG needs special handling for alpha
    if fmt in ("JPEG", "JPG"):
        # If image has transparency, flatten it
        has_alpha = (
            img.mode in ("RGBA", "LA") or
            (img.mode == "P" and "transparency" in img.info)
        )

        if has_alpha:
            # Convert to RGBA so we definitely have an alpha channel to use as mask
            rgba = img.convert("RGBA")
            alpha = rgba.split()[-1]

            background = Image.new("RGB", rgba.size, background_rgb)
            background.paste(rgba, mask=alpha)
            return background

        # No alpha; just ensure RGB
        return img.convert("RGB")

    # Non-JPEG formats: keep as-is (but you can normalize if needed)
    return img


def _content_type_for_format(fmt: str) -> str:
    fmt = (fmt or "JPEG").upper()
    return FORMAT_TO_CONTENT_TYPE.get(fmt, "application/octet-stream")


def upload_image(file_storage, folder='general', create_responsive_versions=False):
    """
    Uploads an image to S3 and returns:
      - a single S3 key (non-responsive), OR
      - a dict of S3 keys (responsive sizes + original)

    Fixes:
      - PNGs with alpha (RGBA) no longer crash when output is JPEG.
      - Uses a reliable ContentType based on detected image format.
    """
    original_filename = secure_filename(file_storage.filename)
    unique_prefix = f"{uuid.uuid4().hex[:8]}"

    try:
        file_storage.seek(0)
        img = Image.open(file_storage)
        img = ImageOps.exif_transpose(img)

        # Pillow format is usually "PNG", "JPEG", etc.
        img_format = (img.format or 'JPEG').upper()
    except Exception as e:
        print(f"Error processing image orientation: {e}")
        return None

    content_type = _content_type_for_format(img_format)

    # Optional: choose a background that matches your theme (cream)
    # background_rgb = (251, 245, 239)  # #fbf5ef
    background_rgb = (255, 255, 255)

    # --- Simple Upload (Non-responsive) ---
    if not create_responsive_versions:
        s3_key = f"{folder}/{unique_prefix}-{original_filename}"
        try:
            in_mem_file = io.BytesIO()
            img_to_save = _normalize_for_save(img, img_format, background_rgb=background_rgb)
            img_to_save.save(in_mem_file, format=img_format)
            in_mem_file.seek(0)

            s3_client.upload_fileobj(
                in_mem_file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": content_type}
            )
            return s3_key
        except Exception as e:
            print(f"Error during single S3 upload: {e}")
            return None

    # --- Responsive Images Logic ---
    keys = {}
    try:
        # Upload responsive versions
        for name, size in RESPONSIVE_SIZES.items():
            img_copy = img.copy()
            img_copy.thumbnail(size)

            in_mem_file = io.BytesIO()
            img_to_save = _normalize_for_save(img_copy, img_format, background_rgb=background_rgb)
            img_to_save.save(in_mem_file, format=img_format)
            in_mem_file.seek(0)

            s3_key = f"{folder}/{unique_prefix}-{name}-{original_filename}"
            s3_client.upload_fileobj(
                in_mem_file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": content_type}
            )
            keys[name] = s3_key

        # Upload the original, full-size image
        in_mem_original = io.BytesIO()
        img_to_save_original = _normalize_for_save(img, img_format, background_rgb=background_rgb)
        img_to_save_original.save(in_mem_original, format=img_format)
        in_mem_original.seek(0)

        s3_key_original = f"{folder}/{unique_prefix}-original-{original_filename}"
        s3_client.upload_fileobj(
            in_mem_original,
            S3_BUCKET,
            s3_key_original,
            ExtraArgs={"ContentType": content_type}
        )
        keys['original'] = s3_key_original

        return keys
    except Exception as e:
        print(f"Error during responsive S3 upload: {e}")
        return None


def generate_presigned_url(s3_key, expiration=3600):
    """
    Generate a pre-signed URL to securely access a private S3 object.
    """
    if not s3_key:
        return None
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return response
    except Exception as e:
        print(f"Error generating presigned URL for key {s3_key}: {e}")
        return None