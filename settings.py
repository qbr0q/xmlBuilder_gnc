import os
from dotenv import load_dotenv


load_dotenv("config.env")

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_DATABASE = os.getenv("database")

validation_path = 'service/builder/validation/Fmba.Aist.SyncDataContract.xsd'

org_id = '770500'

DEVELOP_MODE = True
