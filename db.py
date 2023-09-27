from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DateTime,BLOB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


global base
Base = declarative_base()


class DbStruct:
    class Resources(Base):
        __tablename__ = "resources"
        id = Column("id",Integer,primary_key=True,autoincrement=True)
        member_id = Column("member_id",Integer)
        member_name = Column("member_name",String)
        resource_name = Column("resource_name",String)
        resource_url = Column("resource_url",String)
        resource_file = Column("resource_file",BLOB,default=None)
        file_ext = Column("file_ext",String)
        submittion_date = Column(
            "submission_date", DateTime, default=datetime.datetime.utcnow
        )

        def __init__(self,member_id:int,member_name:str,resource_name:str,resource_url:str=None,resource_file:bytes=None,file_ext:str=None):
            self.member_id = member_id
            self.member_name = member_name
            self.resource_name = resource_name
            if resource_url:
                self.resource_url = resource_url

            else:
                self.resource_file = resource_file
                self.file_ext = file_ext



class BotDb:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///database.db",pool_pre_ping=True)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()