#!/bin/bash

profile=$1
account_id=$2
instance_id=$3
platform=$4

if [ -z "$profile" ] || [ -z "$account_id" ] || [ -z "$instance_id" ]; then
  echo "Usage: $0 <profile> <account_id> <instance_id> [w]"
  echo "option [w] : windows"
  exit 1
fi

python3 get-credential.py $profile $account_id

if [ "$profile" == "p1" ]; then
  bucket_name="snow-cmd-output-1"
elif [ "$profile" == "p2" ]; then
  bucket_name="snow-cmd-output-2"
elif [ "$profile" == "p3" ]; then
  bucket_name="snow-cmd-output-3"
elif [ "$profile" == "p4" ]; then
  bucket_name="snow-cmd-output-4"
elif [ "$profile" == "p5" ]; then
  bucket_name="snow-cmd-output-5"
elif [ "$profile" == "p6" ]; then
  bucket_name="snow-cmd-output-6"
elif [ "$profile" == "p7" ]; then
  bucket_name="snow-cmd-output-7"
fi

if [ "$platform" == "windows" ] || [ "$platform" == "window" ] || [ "$platform" == "win" ] || [ "$platform" == "w" ]; then
  document_name="SG-AWS-RunPowerShellScript"
  script_path="awsrunPowerShellScript/runPowerShellScript/stdout"
else
  document_name="SG-AWS-RunShellScript"
  script_path="awsrunShellScript/runShellScript/stdout"
fi

echo "aws ssm send-command"

output=$(aws ssm send-command \
    --document-name "$document_name" \
    --document-version "1" \
    --targets "[{\"Key\":\"InstanceIds\",\"Values\":[\"$instance_id\"]}]" \
    --parameters '{}' \
    --timeout-seconds 600 \
    --max-concurrency "50" \
    --max-errors "0" \
    --output-s3-bucket-name "$bucket_name" \
    --region ap-northeast-2  --profile sts)

command_id=$(echo $output | jq -r '.Command.CommandId')
echo "$command_id"

if [ "$profile" == "p1" ]; then
    python3 get-credential.py p1 211125417331
elif [ "$profile" == "p2" ]; then
    python3 get-credential.py p2 637423654918
elif [ "$profile" == "p3" ]; then
    python3 get-credential.py p3 654654373995
elif [ "$profile" == "p4" ]; then
    python3 get-credential.py p4 025066275324
elif [ "$profile" == "p5" ]; then
    python3 get-credential.py p5 381491998198
elif [ "$profile" == "p6" ]; then
    python3 get-credential.py p6 026090538040
elif [ "$profile" == "p7" ]; then
    python3 get-credential.py p7 026090538094
fi

for i in {1..10}; do
    echo -n "."
    sleep 1
done
echo

echo "s3api get-object"

aws s3api get-object \
    --bucket "$bucket_name" \
    --key "$command_id/$instance_id/$script_path" \
    sendcmd-$profile-$account_id-$instance_id.txt --profile sts #> /dev/null 2>&1

python3 get-credential.py $profile $account_id
