from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
import os

DB_pswd = os.getenv("db_password")
DB_username = os.getenv("db_username")
DB_host = os.getenv("db_host")
DB_name = os.getenv("db_name")

encoded_password = quote_plus(DB_pswd)
url_db = f'mysql+pymysql://{DB_username}:{encoded_password}@{DB_host}:3306/{DB_name}'

engine = create_engine(url_db, echo=True)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()