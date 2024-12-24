import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone, timedelta

session = boto3.Session()
kms_client = session.client('kms')

tag_key = 'Delete'
tag_value = '3days'

current_time = datetime.now(timezone.utc)

def delete_old_keys():
    # Initialize counters
    total_processed = 0
    total_skipped = 0
    total_marked_for_deletion = 0

    # List all customer managed keys in the region
    try:
        paginator = kms_client.get_paginator('list_keys')
        
        for page in paginator.paginate():
            for key in page['Keys']:
                key_id = key['KeyId']
                total_processed += 1
                print(f"Processing key ID: {key_id} (Key number: {total_processed})")
                
                # Get key metadata 
                try:
                    key_metadata = kms_client.describe_key(KeyId=key_id)
                    
                    # Only process customer managed keys
                    if key_metadata['KeyMetadata']['KeyManager'] == 'CUSTOMER':
                        creation_time = key_metadata['KeyMetadata']['CreationDate']
                        
                        # Check specific tag
                        tags_response = kms_client.list_resource_tags(KeyId=key_id)
                        tags = {tag['TagKey']: tag['TagValue'] for tag in tags_response['Tags']}
                        
                        if tags.get(tag_key) == tag_value:
                            # Check age of the key
                            if current_time - creation_time > timedelta(days=3):
                                # Schedule deletion
                                print(f"Deleting key ID: {key_id} (Older than 3 days with tag)")
                                kms_client.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)
                                total_marked_for_deletion += 1
                            else:
                                print(f"Key ID: {key_id} is not older than 3 days.")
                                total_skipped += 1  # Skipped for not being older than 3 days
                        else:
                            print(f"Key ID: {key_id} does not have the required tag.")
                            total_skipped += 1  # Skipped for missing tag
                    else:
                        print(f"Skipping AWS managed key ID: {key_id}.")
                        total_skipped += 1  # Skipped for AWS managed keys
                
                except ClientError as e:
                    print(f"Error processing key ID: {key_id}. Error: {e}")
                    total_skipped += 1  # Skipped for errors

    except ClientError as e:
        print(f"Failed to list keys. Error: {e}")

    # Print summary of processing results
    print("\nSummary:")
    print(f"Total keys processed: {total_processed}")
    print(f"Total keys skipped: {total_skipped}")
    print(f"Total keys marked for deletion: {total_marked_for_deletion}")

# Run the function to delete old keys
delete_old_keys()
