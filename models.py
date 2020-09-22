import re
from datetime import datetime, time, date

from sqlalchemy import *
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_mixins import AllFeaturesMixin


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


@as_declarative()
class Base(AllFeaturesMixin):
    __abstract__ = True

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True, unique=True)

    @declared_attr
    def __tablename__(self):
        return camel_to_snake(self.__name__)


class User(Base):
    login = Column(String)
    name = Column(String)
    created_on = Column(DateTime, default=datetime.utcnow)
    bot_active = Column(Boolean, default=True)
    notification_time = Column(Time, default=time(20, 0))
    notification_period = Column(Integer)
    last_notified = Column(Date, default=date(1, 1, 1))


class TestResult(Base):
    created_on = Column(DateTime, default=datetime.utcnow)
    value = Column(Integer)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)
    data = Column(JSON)


def connect_to_db():
    engine = create_engine("sqlite:///db.sqlite?check_same_thread=False")
    Session = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(engine)
    session = Session()
    Base.set_session(session)
