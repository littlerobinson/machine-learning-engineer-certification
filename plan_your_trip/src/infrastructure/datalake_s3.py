import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
import logging

logging.getLogger("boto").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

load_dotenv()


class DataLakeS3:
    # Session Boto3 for AWS
    session = None

    # Bucket S3
    bucket = None

    def __init__(self):
        """Initialization of DataLakeS3"""
        try:
            # Initialization of Boto3
            self.session = boto3.Session(
                aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            )
            self.s3_client = self.session.client("s3")
        except KeyError as e:
            raise RuntimeError(f"Missing environment variable: {e}")
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise RuntimeError(f"Credentials not available: {e}")

    def connect(self, bucket_name: str) -> None:
        """method to connect to S3 AWS bucket"""
        try:
            s3 = self.session.resource("s3")
            self.bucket = s3.Bucket(bucket_name)
        except Exception as e:
            print(e)

    def upload_from_dir(self, s3_dir: str, local_dir: str = "./data") -> None:
        """method to upload files from dir to S3 bucket"""
        for subdir, _, files in os.walk(local_dir):
            for file in files:
                full_path = os.path.join(subdir, file)
                try:
                    self.bucket.upload_file(
                        full_path, f"{s3_dir}/{full_path[len(local_dir)+1:]}"
                    )
                    logger.info(
                        f"Successfully uploaded {full_path} to {s3_dir}/{full_path[len(local_dir)+1:]}"
                    )
                except FileNotFoundError:
                    logger.error(f"The file {full_path} was not found")
                except NoCredentialsError:
                    logger.error("Credentials not available")
