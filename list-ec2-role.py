import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def get_role_arn_from_instance_profile(iam_client, instance_profile_arn):
    try:
        instance_profile_name = instance_profile_arn.split('/')[-1]
        response = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
        role_arn = response['InstanceProfile']['Roles'][0]['Arn']
        return role_arn
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Instance Profile {instance_profile_name} cannot be found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        exit(1)
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
        exit(1)
    except ClientError as e:
        print(f"Unexpected error: {e}")
        exit(1)

def main():
    session = boto3.Session()
    ec2_client = session.client('ec2')
    iam_client = session.client('iam')

    try:
        response = ec2_client.describe_instances()
        instances = [instance for reservation in response['Reservations']for instance in reservation['Instances']]
        printed_arns = set()

        for instance in instances:
            instance_id = instance['InstanceId']
            response = ec2_client.describe_iam_instance_profile_associations(
                Filters=[{'Name': 'instance-id', 'Values': [instance_id]}]
            )
            associations = response['IamInstanceProfileAssociations']

            if associations:
                for association in associations:
                    iam_instance_profile_arn = association['IamInstanceProfile']['Arn']
                    role_arn = get_role_arn_from_instance_profile(iam_client, iam_instance_profile_arn)
                    if role_arn:
                        printed_arns.add(role_arn)

        for arn in printed_arns:
            print(f'"{arn}",')

    except ClientError as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
