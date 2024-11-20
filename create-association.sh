#!/bin/bash
aws ssm create-association \
    --name "AWS-GatherSoftwareInventory" \
    --targets "Key=InstanceIds,Values=*" \
    --association-name "SnowInventoryAssociation" \
    --schedule-expression "rate(3 days)" \
    --region ap-northeast-2 --profile sts