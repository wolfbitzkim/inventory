import sys
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import configparser

def get_credential(profile_name, account_id):
    role_name = 'SnowOrganizationAccountAccessRole'
    # session = boto3.Session(profile_name=profile_name)
    sts_client = boto3.client('sts')
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='snow-discovery-session'
    )
    credentials = response['Credentials']
    return credentials

def save_credentials_to_file(credentials, profile='sts'):
    credentials_file = '~/.aws/credentials'
    credentials_file = os.path.expanduser(credentials_file)

    config = configparser.ConfigParser()
    config.read(credentials_file)

    if profile not in config.sections():
        config.add_section(profile)

    config[profile]['aws_access_key_id']= credentials['AccessKeyId']
    config[profile]['aws_secret_access_key']= credentials['SecretAccessKey']
    config[profile]['aws_session_token']= credentials['SessionToken']

    with open(credentials_file, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        profile_name = sys.argv[1]
        if profile_name == "p1":
            account_id = "211125417331"
        elif profile_name == "p2":
            account_id = "637423654918"
        elif profile_name == "p3":
            account_id = "654654373995"
        elif profile_name == "p4":
            account_id = "025066275324"
        elif profile_name == "p5":
            account_id = "381491998198"
        elif profile_name == "p6":
            account_id = "026090538040"
        elif profile_name == "p7":
            account_id = "026090538094"
        else:
            print("Usage: python3 get-credential.py [profile] [account_id]")
            exit(0)
    elif len(sys.argv) == 3:
        profile_name = sys.argv[1]
        account_id = sys.argv[2]
    else:
        print("Usage: python3 get-credential.py [profile] [account_id]")
        exit(0)

    try:
        credentials = get_credential(profile_name, account_id)
        save_credentials_to_file(credentials)
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")
