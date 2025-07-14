import boto3
import os
from werkzeug.utils import secure_filename
import uuid

# Get S3 details from environment variables
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')

# Initialize the S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

def upload_image(file_storage, folder='general'):
    """
    Uploads a file to the S3 bucket and returns its public URL.
    """
    # Create a secure and unique filename
    filename = secure_filename(file_storage.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}-{filename}"
    s3_key = f"{folder}/{unique_filename}"

    try:
        # Upload the file object to S3
        s3_client.upload_fileobj(
            file_storage,
            S3_BUCKET,
            s3_key,
            ExtraArgs={"ContentType": file_storage.content_type}
        )
        # Construct the public URL for the uploaded file
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        return url
    except Exception as e:
        print(f"Error during S3 upload: {e}")
        return None