import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

session = boto3.Session(profile_name='sts', region_name='ap-northeast-2')
ec2_client = session.client('ec2')
iam_client = session.client('iam')

instance_profile_name = 'SnowAmazonSSMForInstancesProfile'

try:
    response = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
    instance_profile_arn = response['InstanceProfile']['Arn']
except iam_client.exceptions.NoSuchEntityException:
    print(f"Instance Profile {instance_profile_name} cannot be found.")
    #exit(1)
except NoCredentialsError:
    print("Credentials not available.")
    exit(1)
except PartialCredentialsError:
    print("Incomplete credentials provided.")
    exit(1)
except ClientError as e:
    print(f"Unexpected error: {e}")
    exit(1)

try:
    response = ec2_client.describe_instances()
    instances = [instance for reservation in response['Reservations']for instance in reservation['Instances']]
    for instance in instances:
        instance_id = instance['InstanceId']
        response = ec2_client.describe_iam_instance_profile_associations(
            Filters=[{'Name': 'instance-id', 'Values': [instance_id]}]
        )
        associations = response['IamInstanceProfileAssociations']

        if not associations:
            print(f'{instance_id} {associations}')
        else:
            for association in associations:
                instance_id = association['InstanceId']
                instance_profile_arn = association['IamInstanceProfile']['Arn']
                print(f'{instance_id} {instance_profile_arn}')

except ClientError as e:
    print(f"Unexpected error: {e}")
    exit(1)