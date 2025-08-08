from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()


## IF MODIFY TABLES GENERATE ALEMBIC VERSION ##

class CabinsDB(Base):
    __tablename__ = "cabins"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False, unique=True)
    hex_color = Column(String(7), nullable=False)


class OperatorsDB(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


class WorkingTimesDB(Base):
    __tablename__ = "working_times"
    id = Column(Integer, primary_key=True, default=1)
    min_start_time = Column(Time, nullable=False)
    max_finish_time = Column(Time, nullable=False)
