import os
from sqlalchemy import create_engine, text
import pandas as pd


# It supposes that you've already a DataFrame called df_final_s3 in your environment


# Make sure to add your credentials in the .env file
username = os.getenv("USERNAME")
password = os.getenv("DB_PWD")
host = os.getenv("HOST_NAME")
port = os.getenv("PORT")
database = os.getenv("DATABASE")

# Create the engine
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

# Write DataFrame to the database
table_name = 'df_final_s3'
df_final_s3.to_sql(table_name, engine, if_exists='replace', index=False)



# Testing the data with a query
query = text("SELECT * FROM df_final_s3 LIMIT 2")
pd.read_sql(query, engine)