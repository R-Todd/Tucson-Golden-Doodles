# app/utils/template_filters.py

from .image_uploader import generate_presigned_url

def setup_template_filters(app):
    """
    Registers custom Jinja2 filters with the Flask application.
    This function is designed to be called from the app factory.
    """
    
    @app.template_filter('s3_url')
    def s3_url_filter(s3_key):
        """
        A Jinja2 filter that takes an S3 key (the string stored in the database)
        and converts it into a temporary, pre-signed URL for secure access.
        
        Usage in template: {{ my_object.image_s3_key | s3_url }}
        """
        if not s3_key:
            return None # Return None if the key is empty or null
        return generate_presigned_url(s3_key)