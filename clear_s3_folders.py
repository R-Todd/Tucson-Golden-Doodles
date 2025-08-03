import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from a .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')

# --- List of folders (S3 prefixes) to clear ---
# IMPORTANT: Ensure these are the correct folder names you want to empty.
FOLDERS_TO_CLEAR = [
    "hero",
    "about",
    "parents",
    "parents_alternates",
    "puppies"
]

def clear_s3_folder(s3_client, bucket_name, folder_name):
    """
    Lists and deletes all objects within a specified folder in an S3 bucket.

    Args:
        s3_client: An initialized boto3 S3 client.
        bucket_name (str): The name of the S3 bucket.
        folder_name (str): The folder (prefix) to clear.
    """
    print(f"\n--- Checking folder: '{folder_name}' ---")

    try:
        # S3 doesn't have real folders, so we list objects with a prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=f"{folder_name}/")

        objects_to_delete = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects_to_delete.append({'Key': obj['Key']})

        if not objects_to_delete:
            print(f"Folder '{folder_name}' is already empty. Nothing to delete.")
            return

        print(f"Found {len(objects_to_delete)} objects to delete in '{folder_name}'.")

        # Boto3's delete_objects can handle up to 1000 keys at a time.
        # We'll batch them just in case a folder has more than 1000 images.
        for i in range(0, len(objects_to_delete), 1000):
            batch = objects_to_delete[i:i+1000]
            print(f"Deleting batch of {len(batch)} objects...")
            s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': batch}
            )

        print(f"✅ Successfully cleared folder '{folder_name}'.")

    except ClientError as e:
        print(f"An AWS error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to orchestrate the S3 folder clearing process.
    """
    print("--- S3 Image Cleanup Script ---")
    
    if not S3_BUCKET or not S3_REGION:
        print("Error: S3_BUCKET_NAME and S3_BUCKET_REGION environment variables must be set.")
        return

    print(f"Target Bucket: {S3_BUCKET}")
    print("This script will delete all objects in the following folders:")
    for folder in FOLDERS_TO_CLEAR:
        print(f"  - {folder}/")

    # --- User Confirmation ---
    confirm = input("\nAre you sure you want to proceed? (yes/no): ").lower()
    if confirm != 'yes':
        print("Operation cancelled by user.")
        return

    try:
        s3_client = boto3.client("s3", region_name=S3_REGION)
        for folder in FOLDERS_TO_CLEAR:
            clear_s3_folder(s3_client, S3_BUCKET, folder)
        
        print("\n--- Cleanup complete! ---")

    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your credentials.")
    except Exception as e:
        print(f"A fatal error occurred: {e}")

if __name__ == '__main__':
    main()
