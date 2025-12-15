import os
from dotenv import load_dotenv


load_dotenv("service/database/config.env")

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_DATABASE = os.getenv("database")

log_file_name = 'xmlBuild.log'
