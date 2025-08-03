# app/utils/template_filters.py

from .image_uploader import generate_presigned_url
# from app import cache  # --- ADD THIS IMPORT ---

def setup_template_filters(app):
    """
    Registers custom Jinja2 filters with the Flask application.
    This function is designed to be called from the app factory.
    """
    
    @app.template_filter('s3_url')
    # --- ADD THIS DECORATOR ---
    # Cache the result for 3000 seconds (50 minutes)
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