import boto3
from botocore.exceptions import (
                            NoCredentialsError, 
                            PartialCredentialsError, 
                            ClientError
                            )

def validate_aws_credentials(
                aws_access_key_id: str,
                aws_secret_access_key: str
                    ):
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        client = session.client('sts')

        response = client.get_caller_identity()

        return {
            "success": True,
            "message": "AWS credentials are valid",
            "status": response['ResponseMetadata']['HTTPStatusCode']
        }
        
    except NoCredentialsError:
        return {
            "success": False,
            "message": "No AWS credentials are found"
        }

    except PartialCredentialsError:
        return {
            "success": False,
            "message": "Incomplete AWS credentials provided."
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']

        if error_code == '403':
            return {
                "success": False,
                "message": "AWS credentials are invalid or access denied.",
                "status": error_code
            }
        else:
            return {
                "success": False,
                "message": "Unexpected error: {e}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": "An error occurred: {e}"
        }