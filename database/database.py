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

from data.env.loader import env

pymysql.install_as_MySQLdb()

# https://docs.sqlalchemy.org/en/20/core/engines.html


# creates the engine and session, nullpool is used to prevent connections from being reused to avoid stale connections, so you don't have to manage them yourself.
engine = create_engine(
	f"{env('DB_TYPE', 'mysql')}://{env('DB_USER', 'username')}:{env('DB_PASSWORD', 'password')}@{env('DB_HOST', "127.0.0.1")}:{env('DB_PORT', "3306")}/{env('DB_NAME', "template")}",
	poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
if not database_exists(engine.url) :
	create_database(engine.url)

conn = engine.connect()


class Base(DeclarativeBase) :
	pass


# creates tables
class Users(Base) :
	__tablename__ = "users"
	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
	messages: Mapped[int] = mapped_column(BigInteger, default=0)
	xp: Mapped[int] = mapped_column(BigInteger, default=0)


class Levels(Base) :
	__tablename__ = "levels"
	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	guildid: Mapped[int] = mapped_column(BigInteger)
	role_id: Mapped[int] = mapped_column(BigInteger)
	xp_required: Mapped[int] = mapped_column(BigInteger)


class Channels(Base) :
	__tablename__ = "channels"
	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	guildid: Mapped[int] = mapped_column(BigInteger)
	channelid: Mapped[int] = mapped_column(BigInteger)



class database :
	@staticmethod
	def create() :
		Base.metadata.create_all(engine)
		print("Database built")



def create_bot_database() :
	Base.metadata.create_all(engine)


def drop_bot_database() :
	if os.getenv('DISCORD_TOKEN') is not None :
		raise Exception("You cannot drop the database while the bot is in production")
	Session = sessionmaker(bind=engine)
	session = Session()
	session.close_all()
	Base.metadata.drop_all(engine)
