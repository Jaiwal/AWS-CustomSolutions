import boto3
from botocore.exceptions import ClientError

def check_secret_exists(secret_name, region_name='us-east-2'):
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        client.describe_secret(SecretId=secret_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        else:
            raise e

def delete_secret(secret_name, region_name='us-east-2'):
    client = boto3.client('secretsmanager', region_name=region_name)

    if not check_secret_exists(secret_name, region_name):
        print(f"Error: Secret {secret_name} does not exist.")
        return

    try:
        response = client.delete_secret(
            SecretId=secret_name,
            ForceDeleteWithoutRecovery=True
        )
        print(f"Secret {secret_name} deleted permanently.")
    except ClientError as e:
        print(f"Unexpected error: {e}")

secret_name = 'test-secret'

delete_secret(secret_name)

delete_secret(secret_name)



