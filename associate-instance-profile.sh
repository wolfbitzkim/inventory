
#!/bin/bash
instance_id=$1
aws ec2 associate-iam-instance-profile --instance-id $instance_id --iam-instance-profile Name=SnowAmazonSSMForInstancesProfile --profile sts
