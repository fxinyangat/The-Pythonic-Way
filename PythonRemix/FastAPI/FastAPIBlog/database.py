from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote_plus

db_username = "root"
db_password = "Test@1234"
db_host = "127.0.0.1"
db_name = "blog_app"

encoded_password = quote_plus(db_password)
engine = create_engine(f'mysql+pymysql://{db_username}:{encoded_password}@{db_host}:3306/{db_name}')


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()