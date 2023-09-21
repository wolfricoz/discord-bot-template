import os
from datetime import datetime
from typing import List, Optional

import pymysql
from sqlalchemy import create_engine, DateTime, ForeignKey, String, select, BigInteger, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
pymysql.install_as_MySQLdb()

# https://docs.sqlalchemy.org/en/20/core/engines.html
load_dotenv('.env')
dblink = os.getenv('DB')
engine = create_engine(dblink, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
if not database_exists(engine.url):
    create_database(engine.url)

conn = engine.connect()


class Base(DeclarativeBase):
    pass

# creates tables
class Users(Base):
    __tablename__ = "users"
    uid: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    messages: Mapped[int] = mapped_column(BigInteger, default=0)
    xp: Mapped[int] = mapped_column(BigInteger ,default=0)

class Levels(Base):
    __tablename__ = "levels"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guildid: Mapped[int] = mapped_column(BigInteger)
    role_id: Mapped[int] = mapped_column(BigInteger)
    xp_required: Mapped[int] = mapped_column(BigInteger)

class Channels(Base):
    __tablename__ = "channels"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guildid: Mapped[int] = mapped_column(BigInteger)
    channelid: Mapped[int] = mapped_column(BigInteger)


class database:
    def create(self):
        Base.metadata.create_all(engine)
