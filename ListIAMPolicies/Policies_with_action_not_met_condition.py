
import boto3

# Initialize a session using Amazon IAM
session = boto3.Session()
iam_client = session.client('iam')

def check_policy_for_action(policy_document, action_to_check):
    """Check if the specified action is present in the policy document."""
    statements = policy_document.get('Statement', [])
    for statement in statements:
        if isinstance(statement, dict):
            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]  # Convert to list if it's a single string
            
            if action_to_check in actions:
                return True
    return False

def check_policy_for_excluded_resource(policy_document, excluded_string):
    """Check if any resource contains the excluded string."""
    statements = policy_document.get('Statement', [])
    for statement in statements:
        if isinstance(statement, dict):
            resources = statement.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]  # Convert to list if it's a single string
            
            for resource in resources:
                if excluded_string in resource:
                    return True
    return False

def get_all_users_with_ssm_start_session_excluding_resource():
    # Set to hold unique ARNs of policies with ssm:StartSession action excluding specific resource
    policies_with_ssm_start_session = set()
    action_to_check = "ssm:StartSession"
    excluded_string = "SSM-SessionManagerRunShell"

    # Get a list of all IAM users
    users = iam_client.list_users()

    for user in users['Users']:
        user_name = user['UserName']

        # Check attached managed policies for the user
        attached_policies = iam_client.list_attached_user_policies(UserName=user_name)
        for policy in attached_policies['AttachedPolicies']:
            policy_arn = policy['PolicyArn']

            # Get the policy document
            policy_version = iam_client.get_policy(PolicyArn=policy_arn)
            default_version_id = policy_version['Policy']['DefaultVersionId']
            policy_document = iam_client.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=default_version_id
            )

            # Check conditions
            if (check_policy_for_action(policy_document['PolicyVersion']['Document'], action_to_check) and 
                not check_policy_for_excluded_resource(policy_document['PolicyVersion']['Document'], excluded_string)):
                policies_with_ssm_start_session.add((user_name, policy_arn, 'Managed Policy'))

        # Check inline policies for the user
        inline_policies = iam_client.list_user_policies(UserName=user_name)
        for inline_policy_name in inline_policies['PolicyNames']:
            inline_policy_document = iam_client.get_user_policy(
                UserName=user_name,
                PolicyName=inline_policy_name
            )

            # Check conditions
            if (check_policy_for_action(inline_policy_document['PolicyDocument'], action_to_check) and 
                not check_policy_for_excluded_resource(inline_policy_document['PolicyDocument'], excluded_string)):
                inline_policy_arn = f"Inline Policy - {user_name}: {inline_policy_name}"
                policies_with_ssm_start_session.add((user_name, inline_policy_arn, 'Inline Policy'))

    return policies_with_ssm_start_session

# Run the function and print results
resulting_policies = get_all_users_with_ssm_start_session_excluding_resource()
print("\nPolicies with 'ssm:StartSession' action (excluding specified resource):")
for user_name, arn, policy_type in resulting_policies:
    print(f"User: {user_name}, Policy ARN: {arn}, Type: {policy_type}")


