import sys
import json
import boto3

if len(sys.argv) != 2:
    print("Usage: python3 read-role-details.py [role_name]")
    exit(1)
else:
    role_name = sys.argv[1]

profile_name = 'sts'
region_name = 'ap-northeast-2'
session = boto3.Session(profile_name=profile_name, region_name=region_name)

iam_client = session.client('iam')
inline_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
for policy_name in inline_policies:
    policy_document = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)['PolicyDocument']
    print(f"인라인 정책 이름: {policy_name}")
    print("정책 내용:")
    print(json.dumps(policy_document, indent=4))

attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
for attached_policy in attached_policies:
    policy_arn = attached_policy['PolicyArn']
    policy_name = attached_policy['PolicyName']
    policy_versions = iam_client.list_policy_versions(PolicyArn=policy_arn)['Versions']
    default_version = next(version for version in policy_versions if version['IsDefaultVersion'])
    policy_version_id = default_version['VersionId']
    policy_document = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version_id)['PolicyVersion']['Document']
    print(f"관리형 정책 이름: {policy_name}")
    print("정책 내용:")
    print(json.dumps(policy_document, indent=4))

response = iam_client.get_role(RoleName=role_name)
trust_policy = response['Role']['AssumeRolePolicyDocument']
print("신뢰 관계 정책:")
print(json.dumps(trust_policy, indent=4))
