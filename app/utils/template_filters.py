# app/utils/template_filters.py

from .image_uploader import generate_presigned_url
# The 'from app import cache' line should be removed from the top of the file.

def setup_template_filters(app):
    """
    Registers custom Jinja2 filters with the Flask application.
    This function is designed to be called from the app factory.
    """
    # --- ADD THE IMPORT HERE ---
    # This ensures 'cache' is defined before the decorator uses it,
    # and it avoids the circular import error.
    from app import cache
    
    @app.template_filter('s3_url')
    @cache.memoize(timeout=3000)
    def s3_url_filter(s3_key):
        """
        A Jinja2 filter that takes an S3 key and converts it into a
        temporary, pre-signed URL. The result is cached to prevent
        redundant API calls.
        """
        if not s3_key:
            return None
        return generate_presigned_url(s3_key)