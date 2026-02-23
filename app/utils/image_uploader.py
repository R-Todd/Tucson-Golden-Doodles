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

# Base responsive sizes (used for most uploads)
RESPONSIVE_SIZES_BASE = {
    "small": (480, 480),
    "medium": (800, 800),
    "large": (1200, 1200),
}

# Hero gets an additional XL size for premium sharpness on desktop
RESPONSIVE_SIZES_HERO = {
    **RESPONSIVE_SIZES_BASE,
    "xl": (1920, 1920),
}

# Minimum acceptable resolution for hero uploads (long edge)
HERO_MIN_LONG_EDGE_PX = 1600

# JPEG tuning (premium, still reasonable file sizes)
JPEG_QUALITY = 88

# Map Pillow formats to HTTP Content-Types
FORMAT_TO_CONTENT_TYPE = {
    "JPEG": "image/jpeg",
    "JPG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}


def _get_lanczos_resample():
    """
    Pillow compatibility helper:
    Newer Pillow uses Image.Resampling.LANCZOS, older versions use Image.LANCZOS.
    """
    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS


LANCZOS = _get_lanczos_resample()


def _normalize_for_save(img: Image.Image, fmt: str, background_rgb=(255, 255, 255)) -> Image.Image:
    """
    Ensures the PIL image is compatible with the target format.

    - JPEG does not support alpha, so RGBA/LA/P w/transparency must be flattened onto a background.
    - For JPEG, we also guarantee RGB mode.
    - For PNG, we keep alpha if present.
    """
    fmt = (fmt or "JPEG").upper()

    if fmt in ("JPEG", "JPG"):
        has_alpha = (
            img.mode in ("RGBA", "LA")
            or (img.mode == "P" and "transparency" in img.info)
        )

        if has_alpha:
            rgba = img.convert("RGBA")
            alpha = rgba.split()[-1]

            background = Image.new("RGB", rgba.size, background_rgb)
            background.paste(rgba, mask=alpha)
            return background

        return img.convert("RGB")

    return img


def _content_type_for_format(fmt: str) -> str:
    fmt = (fmt or "JPEG").upper()
    return FORMAT_TO_CONTENT_TYPE.get(fmt, "application/octet-stream")


def _save_image_to_bytes(img: Image.Image, fmt: str) -> io.BytesIO:
    """
    Save image to BytesIO with format-specific quality tuning.
    """
    fmt = (fmt or "JPEG").upper()
    buf = io.BytesIO()

    if fmt in ("JPEG", "JPG"):
        img.save(
            buf,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True
        )
    else:
        # PNG/WEBP/GIF: keep defaults; PNG can be optimized as well
        # (optimize works for PNG but can be slower; enable if you want)
        if fmt == "PNG":
            img.save(buf, format="PNG", optimize=True)
        else:
            img.save(buf, format=fmt)

    buf.seek(0)
    return buf


def upload_image(file_storage, folder='general', create_responsive_versions=False):
    """
    Uploads an image to S3 and returns:
      - a single S3 key (non-responsive), OR
      - a dict of S3 keys (responsive sizes + original)

    Enhancements:
      - Hero uploads get an XL (1920) version for crisp desktop hero rendering
      - LANCZOS resampling for highest resize quality
      - JPEG quality tuning (quality=88, optimize, progressive)
      - Minimum resolution guard for hero uploads (rejects too-small images)
      - PNG alpha flattening when saving JPEG (prevents RGBA -> JPEG crash)
      - ContentType derived from detected format
    """
    original_filename = secure_filename(file_storage.filename)
    unique_prefix = f"{uuid.uuid4().hex[:8]}"

    try:
        file_storage.seek(0)
        img = Image.open(file_storage)
        img = ImageOps.exif_transpose(img)
        img_format = (img.format or 'JPEG').upper()
    except Exception as e:
        print(f"Error processing image orientation: {e}")
        return None

    # Optional: choose a background that matches your theme (cream)
    # background_rgb = (251, 245, 239)  # #fbf5ef
    background_rgb = (255, 255, 255)

    # Minimum resolution guard (hero only)
    if folder == "hero":
        w, h = img.size
        long_edge = max(w, h)
        if long_edge < HERO_MIN_LONG_EDGE_PX:
            print(
                f"Hero image rejected: resolution too small ({w}x{h}). "
                f"Please upload at least {HERO_MIN_LONG_EDGE_PX}px on the long edge for a crisp hero."
            )
            return None

    content_type = _content_type_for_format(img_format)

    # Select responsive sizes (hero gets XL)
    responsive_sizes = RESPONSIVE_SIZES_HERO if folder == "hero" else RESPONSIVE_SIZES_BASE

    # --- Simple Upload (Non-responsive) ---
    if not create_responsive_versions:
        s3_key = f"{folder}/{unique_prefix}-{original_filename}"
        try:
            img_to_save = _normalize_for_save(img, img_format, background_rgb=background_rgb)
            in_mem_file = _save_image_to_bytes(img_to_save, img_format)

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
        for name, size in responsive_sizes.items():
            img_copy = img.copy()

            # High-quality resize (LANCZOS)
            img_copy.thumbnail(size, resample=LANCZOS)

            img_to_save = _normalize_for_save(img_copy, img_format, background_rgb=background_rgb)
            in_mem_file = _save_image_to_bytes(img_to_save, img_format)

            s3_key = f"{folder}/{unique_prefix}-{name}-{original_filename}"
            s3_client.upload_fileobj(
                in_mem_file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": content_type}
            )
            keys[name] = s3_key

        # Upload the original, full-size image
        img_to_save_original = _normalize_for_save(img, img_format, background_rgb=background_rgb)
        in_mem_original = _save_image_to_bytes(img_to_save_original, img_format)

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