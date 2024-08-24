import sqlalchemy as sa
from sqlalchemy import orm,engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime as dt
from sqlalchemy.schema import MetaData

Session = sessionmaker(twophase=True)

binds = {}

class DbSqlB:
    base        = declarative_base()
    #fast_executemany=True,
    #pool_size=10,
    #max_overflow=2,
    #pool_recycle=300,
    #pool_pre_ping=True,
    #pool_use_lifo=True
    def __init__(self,ConnectionString,**kwargs):
        config_1 = {"sqlalchemy.url":ConnectionString,"sqlalchemy.echo": False}
        self.engine                 = engine_from_config({**config_1,**kwargs})
        # self.base.metadata.drop_all(bind=self.engine)
        # self.base.metadata.create_all(bind=self.engine)
        #self.engine                 = sa.create_engine(ConnectionString) if not fast_executemany else sa.create_engine(ConnectionString,fast_executemany=True)
        self.session                = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=self.engine))
        self.orm_session            = orm.scoped_session(orm.sessionmaker())(bind=self.engine)
        # self.base.metadata.bind     = self.engine
        self.base        = declarative_base(metadata=MetaData(bind=self.engine))
        self.base.query             = self.session.query_property()
        #self.base.metadata     = MetaData(bind=self.engine) 

    def create_all(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        self.base.metadata.create_all(self.engine)
    
    def update_engine(self,cls):
        global Session
        global binds
        binds[cls] = self.engine
        Session.configure(binds=binds)
        Session = Session()
        self.base.query = Session.query_property()


class DbSqlA:
    base        = declarative_base()
    #fast_executemany=True,
    #pool_size=10,
    #max_overflow=2,
    #pool_recycle=300,
    #pool_pre_ping=True,
    #pool_use_lifo=True
    def __init__(self,ConnectionString,**kwargs):
        self.engine                 = sa.create_engine(ConnectionString, **kwargs)
        self.session                = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=self.engine))
        self.base.query             = self.session.query_property()
        self.orm_session            = orm.scoped_session(orm.sessionmaker())(bind=self.engine)
        self.base.metadata.bind     = self.engine    

    def create_all(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        self.base.metadata.create_all(self.engine)


def tblUts(db):
    class auxDB:
        id      = sa.Column(sa.Integer,primary_key=True,autoincrement=True)

        def save(self):
            try:
                if not self.id:
                    db.session.add(self)
                db.session.commit()
            except:
                db.session.rollback()
                raise

        def delete(self):
            db.session.rollback()
            db.session.delete(self)
            db.session.commit()
    
    
    return auxDB

