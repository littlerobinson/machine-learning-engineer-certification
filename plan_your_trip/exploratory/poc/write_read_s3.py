import os
from dotenv import load_dotenv 
from io import BytesIO
import pandas as pd
import boto3


##### Don't forget to add your credentials in the .env file
load_dotenv()


# Configure AWS connection
session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
s3 = session.resource('s3')


# Uploading the file to S3
s3.Bucket('bucket-name').upload_file('file-path', 'file-name-and-path')


# Downloading the file from S3
try:
    obj = s3.Object('bucketdsfsod07', 'data-kayak-project/df_complete.csv')
    df_s3 = pd.read_csv(BytesIO(obj.get()['Body'].read()))
    print("File downloaded successfully")
except Exception as e:
    print(e)

# Checking the content of the file
df_s3.head(2)