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
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server=tcp:{databaseServer},1433;"
        f"Database={databaseName};"
        f"Uid={databaseUsername};"
        f"Pwd={databasePassword};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
