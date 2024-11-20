import boto3
import json
import sys
import subprocess

if len(sys.argv) != 4:
    print("Usage: {} [profile] [account_id] [role_name]".format(sys.argv[0]))
    sys.exit(1)

profile = sys.argv[1]
account_id = sys.argv[2]
role_name = sys.argv[3]
subprocess.run(["python3", "get-credential.py", profile, account_id])
print(f"--- Role : {role_name} ---")
profile_name = 'default'
region_name = 'ap-northeast-2'
session = boto3.Session(profile_name='sts', region_name=region_name)

iam_client = session.client('iam')
policy_arn = f'arn:aws:iam::{account_id}:policy/SSIMSnowSSMSendCommandPolicy'

try:
    response = iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    print(f"Policy {policy_arn} has been attached to role {role_name}.")
except Exception as e:
    print(f"An error occurred: {e}")
try:
    response = iam_client.list_attached_role_policies(
        RoleName=role_name
    )
    print(f"Attached managed policies for role {role_name}:")
    for policy in response['AttachedPolicies']:
        print(f"- {policy['PolicyName']} (ARN: {policy['PolicyArn']})")
except Exception as e:
    print(f"An error occurred while listing managed policies: {e}")
try:
    inline_policies = iam_client.list_role_policies(
        RoleName=role_name
    )
    print(f"Inline policies for role {role_name}:")
    for policy_name in inline_policies['PolicyNames']:
        policy = iam_client.get_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )
        print(f"- {policy_name}")
except Exception as e:
    print(f"An error occurred while listing inline policies: {e}")

response = iam_client.get_role(RoleName=role_name)
trust_policy = response['Role']['AssumeRolePolicyDocument']
print("현재 신뢰 관계 정책:")
print(json.dumps(trust_policy, indent=4))
new_statement = {
    "Effect": "Allow",
    "Principal": {
        "Service": "ec2.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
}
exists = any(
    statement.get("Effect") == new_statement["Effect"]and
    statement.get("Principal") == new_statement["Principal"]and
    statement.get("Action") == new_statement["Action"]
    for statement in trust_policy.get("Statement", [])
)
if not exists:
    trust_policy['Statement'].append(new_statement)
    response = iam_client.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(trust_policy)
    )
    updated_response = iam_client.get_role(RoleName=role_name)
    updated_trust_policy = updated_response['Role']['AssumeRolePolicyDocument']
    print("업데이트된 신뢰 관계 정책:")
    print(json.dumps(updated_trust_policy, indent=4))