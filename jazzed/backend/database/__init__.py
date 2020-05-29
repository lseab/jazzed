from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine

db_config = {
    'drivername': 'sqlite',
    'database': 'testDB'
}

db_engine = create_engine(URL(**db_config))
Session = sessionmaker(bind=db_engine)
Base = declarative_base()
session = Session()