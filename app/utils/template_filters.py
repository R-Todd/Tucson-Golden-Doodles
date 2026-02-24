from .image_uploader import generate_presigned_url

DEFAULT_PRESIGN_EXPIRES = 3600
DEFAULT_S3_URL_CACHE_TTL = 3000  # keep your current behavior

def setup_template_filters(app, cache):
    """
    Registers custom Jinja2 filters with the Flask application.
    Designed to be called from the app factory.
    """

    @app.template_filter("s3_url")
    @cache.memoize(timeout=app.config.get("S3_URL_CACHE_TTL", DEFAULT_S3_URL_CACHE_TTL))
    def s3_url_filter(s3_key):
        if not s3_key:
            return None

        expires = app.config.get("S3_PRESIGN_EXPIRES", DEFAULT_PRESIGN_EXPIRES)
        return generate_presigned_url(s3_key, expiration=expires)