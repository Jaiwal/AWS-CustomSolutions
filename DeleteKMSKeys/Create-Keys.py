import boto3
import json

kms_client = boto3.client('kms', region_name='us-east-1')

def create_kms_keys(num_keys):
    for i in range(num_keys):
        try:
            # Define the key policy
            key_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Enable IAM User Permissions",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::account-id:root"
                        },
                        "Action": "kms:*",
                        "Resource": "*"
                    }
                ]
            }
            response = kms_client.create_key(
                Policy=json.dumps(key_policy), 
                Description=f"My KMS key {i + 1}",
                KeyUsage='ENCRYPT_DECRYPT',
                Origin='AWS_KMS'
            )

            key_id = response['KeyMetadata']['KeyId']
            print(f"Created KMS key: {key_id}")

            kms_client.tag_resource(
                KeyId=key_id,
                Tags=[
                    {
                        'TagKey': 'Delete',
                        'TagValue': '3days'
                    }
                ]
            )
            print(f"Tagged KMS key {key_id} with Delete:3days")

        except Exception as e:
            print(f"Error creating or tagging KMS key {i + 1}: {e}")

if __name__ == "__main__":
    create_kms_keys(500)
