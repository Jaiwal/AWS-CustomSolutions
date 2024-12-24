import botocore
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone, timedelta

# Initialize a session using Amazon KMS
session = boto3.Session()
kms_client = session.client('kms')

# Define the tag key and value to look for
tag_key = 'Delete'
tag_value = '3days'

# Get the current time
current_time = datetime.now(timezone.utc)

# Function to delete keys older than 3 days with the specified tag
def delete_old_keys():
    # List all keys in the region
    try:
        paginator = kms_client.get_paginator('list_keys')
        key_count = 0
        
        for page in paginator.paginate():
            for key in page['Keys']:
                key_id = key['KeyId']
                key_count += 1
                print(f"Processing key ID: {key_id} (Key number: {key_count})")
                
                # Get key metadata to check creation date and tags
                try:
                    key_metadata = kms_client.describe_key(KeyId=key_id)
                    creation_time = key_metadata['KeyMetadata']['CreationDate']
                    
                    # Check if the key has the specified tag
                    tags_response = kms_client.list_resource_tags(KeyId=key_id)
                    tags = {tag['TagKey']: tag['TagValue'] for tag in tags_response['Tags']}
                    
                    if tags.get(tag_key) == tag_value:
                        # Check if the key is older than 3 days
                        if current_time - creation_time > timedelta(days=3):
                            # Schedule the key for deletion
                            print(f"Deleting key ID: {key_id} (Older than 3 days with tag)")
                            kms_client.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)
                        else:
                            print(f"Key ID: {key_id} is not older than 3 days.")
                    else:
                        print(f"Key ID: {key_id} does not have the required tag.")
                
                except ClientError as e:
                    print(f"Error processing key ID: {key_id}. Error: {e}")

    except ClientError as e:
        print(f"Failed to list keys. Error: {e}")

# Run the function to delete old keys
delete_old_keys()
