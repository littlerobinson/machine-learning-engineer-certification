from sqlalchemy import create_engine
import os

# Singleton to connect to database 
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connect_to_database()
        return cls._instance

    def connect_to_database(self):
        try:
            self.db_username = os.environ['DB_USERNAME']
            self.db_password = os.environ['DB_PASSWORD']
            self.db_hostname = os.environ['DB_HOSTNAME']
            self.db_name = os.environ['DB_NAME']
            self.db_port = os.environ['DB_PORT']

            self.engine = create_engine(f"postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}", echo=True)
        except KeyError as e:
            raise RuntimeError(f"Missing environment variable: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create database engine: {e}")

    def get_engine(self):
        return self.engine