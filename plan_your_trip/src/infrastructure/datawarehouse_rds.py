import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
from sqlalchemy import create_engine, text
from src.utils.database_connection import DatabaseConnection
import logging
from dotenv import load_dotenv

logging.getLogger('boto').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

load_dotenv()

class DataWarehouseRDS():

    # S3 client
    s3_client = None

    def __init__(self):
        """Initialization of DataWarehouseRDS"""

        try:
            # Initialization of Boto3
            session = boto3.Session(
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
            )
            self.s3_client = session.client('s3')

        except KeyError as e:
            raise RuntimeError(f"Missing environment variable: {e}")
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise RuntimeError(f"Credentials not available: {e}")
        # Connect to sql database
        try:
            db_instance = DatabaseConnection()
            self.engine = db_instance.get_engine()
            # self.engine = create_engine(f"postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}", echo=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create database engine: {e}")

    def dataframe_to_rds(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace') -> None:
        """
        Write a DataFrame to an RDS database table.

        Args:
        - df: DataFrame to be written to the database.
        - table_name: Name of the table in the database where the DataFrame will be written.
        - if_exists: What to do if the table already exists in the database.
          Options include 'fail', 'replace', or 'append'. Default is 'replace'.

        Raises:
        - RuntimeError: If the DataFrame could not be written to the database.
        """
        try:
            df_final_s3.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
        except Exception as e:
            raise RuntimeError(f"Failed to write DataFrame to RDS: {e}")

    def list_bucket_files(self, bucket_name:str, s3_dir: str) -> list[str]:
        """
        Lists all files in a given S3 bucket with an optional prefix.
        
        Args:
        - bucket_name: S3 bucket name.
        - s3_dir: Optional prefix to filter files.
        
        Returns:
        - List of file paths in the bucket.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_dir)
            return [content['Key'] for content in response.get('Contents', [])]

        except ClientError as e:
            raise RuntimeError(f"Failed to list files in bucket {bucket_name} with prefix '{directory_prefix}': {e}")

    def read_csv_from_s3(self, bucket_name: str, key: str) -> pd.DataFrame:
        """
        Read a CSV file from an S3 bucket and load it into a DataFrame.
        
        Args:
        - bucket_name: Name of the S3 bucket.
        - key: Path to the file in the bucket.
        
        Returns:
        - DataFrame containing the CSV file data.
        """
        csv_obj = self.s3_client.get_object(Bucket=bucket_name, Key=key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        return pd.read_csv(StringIO(csv_string))

    def read_json_from_s3(self, bucket_name: str, key: str) -> pd.DataFrame:
        """
        Read a JSON file from an S3 bucket and load it into a DataFrame.
        
        Args:
        - bucket: Name of the S3 bucket.
        - key: Path to the file in the bucket.
        
        Returns:
        - DataFrame containing the JSON file data.
        """
        json_obj = self.s3_client.get_object(Bucket=bucket_name, Key=key)
        body = json_obj['Body']
        json_string = body.read().decode('utf-8')
        return pd.read_json(StringIO(json_string))

    def clean_and_save_forecast_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the DataFrame by adding an 'id' column and save it to the 'forecasts' table in the database.
        Create a score for forecast

        Args:
        - df: The original DataFrame containing forecast data.

        Returns:
        - A new DataFrame with an 'id' column and selected columns.
        """
        # create a new column id
        df['id'] = np.arange(0, len(df))
        # new_df = df[['id', 'city_id', 'lat', 'lon', 'dt', 'temp_day', 'humidity', 'weather_main', 'clouds', 'rain', 'wind_speed']]
        df_weather = df[['city', 'city_id', 'lat', 'lon', 'feels_like_day', 'humidity', 'clouds', 'pop', 'wind_speed']]

        # Définir les poids
        weights = {
            'feels_like_day': 1.0, # Positive weight
            'humidity': -0.1, # Negative weight
            'clouds': -0.1, # Negative weight
            'pop': -1.0, # Negative weight
            'wind_speed': -0.1 # Negative weight
        }

        # Calculer les scores pondérés
        df_weather_score = df_weather.copy()
        df_weather['forecast_score'] = (df_weather['feels_like_day'] * weights['feels_like_day'] +
                                df_weather['humidity'] * weights['humidity'] +
                                df_weather['clouds'] * weights['clouds'] +
                                df_weather['pop'] * weights['pop'] +
                                df_weather['wind_speed'] * weights['wind_speed'])
        df_weather.to_sql("forecasts", self.engine, if_exists='replace', index=False) # Index false, do not write dataframe index to bdd
        return df_weather

    def clean_and_save_accomodation_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the DataFrame by adding an 'id' column and save it to the 'accomodations' table in the database.

        Args:
        - df: The original DataFrame containing accomodation data.

        Returns:
        - A new DataFrame with an 'id' column and selected columns.
        """
        # create a new column id
        df['id'] = np.arange(0, len(df))
        # Get latitude and longitude in 2 columns
        df[['lat', 'lon']] = df['gps_coordinates'].str.split(',', expand=True).astype(float)
        # df['lat'] = df['gps_coordinates'].str.split(',')[0]
        # df['long'] = df['gps_coordinates'].str.split(',')[1]

        # Relation made with 'search_city'

        new_df = df[['id', 'city_id', 'name', 'score', 'description', 'gps_coordinates', 'lat', 'lon']]
        new_df.to_sql("accomodations", self.engine, if_exists='replace', index=False)
        return new_df


    def clean_and_save_city_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the DataFrame by adding an 'id' column and save it to the 'cities' table in the database.

        Args:
        - df: The original DataFrame containing city data.

        Returns:
        - A new DataFrame with an 'id' column and selected columns.
        """
        # create a new column id
        df['id'] = np.arange(0, len(df))
        new_df = df[['id', 'name', 'lat', 'lon']]
        new_df.to_sql("cities", self.engine, if_exists='replace', index=False)
        return new_df

    def get_dataframes_from_s3_dir(self, bucket_name:str, s3_dir: str = None) -> tuple[list[pd.DataFrame], list[pd.DataFrame]]:
        """
        Retrieves CSV and JSON files from an S3 bucket directory and transforms them into DataFrames.
        
        Args:
        - bucket_name: S3 bucket name.
        - s3_dir: Optional prefix to filter files.
        
        Returns:
        - df_list_csv: List of DataFrames for CSV files.
        - df_list_json: List of DataFrames for JSON files.
        """
        # Fetch files from bucket
        key = s3_dir + '/' + filename
        files = [self.s3_client.get_object(Bucket=bucket_name, Key=key)]

        # Filter files type : CSV and JSON
        csv_files = [f for f in files if f.endswith('.csv')]
        json_files = [f for f in files if f.endswith('.json')]

        try:
            # Read files and convert them in dataframes
            df_list_csv = [self.read_csv_from_s3(bucket_name, file) for file in csv_files]
            df_list_json = [self.read_json_from_s3(bucket_name, file) for file in json_files]

            return df_list_csv, df_list_json
        except ClientError as e:
            raise RuntimeError(f"Failed to read file from bucket {bucket_name}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to process file : {e}")

    def fetch_city_data(self):
        # Exemple de requête pour extraire les données de la base de données
        query = "SELECT * FROM cities"
        df = pd.read_sql(query, self.engine)
        return df
