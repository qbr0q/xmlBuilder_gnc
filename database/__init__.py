from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv("database/config.env")

DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    user=os.getenv("user"), password=os.getenv("password"), host=os.getenv("host"),
    port=os.getenv("port"), database=os.getenv("database")
)
engine = create_engine(DATABASE_URL)
