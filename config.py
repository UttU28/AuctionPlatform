import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')  # For session management, CSRF protection, etc.

class AzureSQLConfig(Config):
    databaseServer='auctionsql.database.windows.net'
    databaseName='auctionsqldb'
    databaseUsername='iAmRoot'
    databasePassword='Qwerty@213'
    connectionString = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server=tcp:{databaseServer},1433;"
        f"Database={databaseName};"
        f"Uid={databaseUsername};"
        f"Pwd={databasePassword};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

class AzureBLOBConfig(Config):
    AZURE_CONNECTION_STRING='DefaultEndpointsProtocol=https;AccountName=dicestorage02;AccountKey=OFusrDHbeLjeipF0m836T13AakwgBzaX7gbAl+Cjw46N1K/dEEHvVbiC2Mw+JYE67v+2KNqg7BAN+AStPE7SGw==;EndpointSuffix=core.windows.net'
    CONTAINER_NAME='resume-data'
    # AZURE_CONNECTION_STRING = os.getenv('blobConnectionString')
    # CONTAINER_NAME = os.getenv('resumeContainer')