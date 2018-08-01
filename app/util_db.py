import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DBBase = declarative_base()
DBSession = sessionmaker()


def open(db_url):
	db_engine = create_engine(db_url, echo=False)
	DBBase.metadata.create_all(db_engine)
	DBSession.configure(bind=db_engine)
	# DBSession = sessionmaker(bind=db_engine)
	return DBSession()

