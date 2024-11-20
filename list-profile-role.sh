#!/bin/bash
instance_profiles=$(aws iam list-instance-profiles --query 'InstanceProfiles[*].{Name:InstanceProfileName,Arn:Arn,Roles:Roles}' --output json --profile sts)
if [ -z "$instance_profiles" ]; then
  echo "No instance profiles found."
  exit 0
fi
if ! command -v jq &> /dev/null; then
  echo "jq is required but not installed. Please install jq and try again."
  exit 1
fi
echo "Instance Profile ARN and Role ARN:"
echo "-----------------------------------"
echo "$instance_profiles" | jq -r '.[]| "\(.Name) \t\(.Roles[0].RoleName)"' | awk '{printf "%-40s %-40s\n", $1, $2}'
