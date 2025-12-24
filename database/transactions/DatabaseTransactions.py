"""This is the base class for ALL database transactions, it contains the connection to the database and basic functions"""
import logging

import pymysql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from database.database import engine


class DatabaseTransactions:
	# We use expire_on_commit=False to prevent objects from being expired after commit; this allows us to still access their attributes without needing to re-query the database.
	sessionmanager = sessionmaker(bind=engine, expire_on_commit=False)
	# Sessions can be done two ways; either we use a variable like self.session or you can use 'with sessionmaker as session:'.
	# It's recommended to use the 'with' method for most cases to ensure proper session management.

	# Create a new session, you want to create a new session for each transaction to ensure data integrity and avoid conflicts.
	# Using a single or very few transactions can cause your connection to lock up when you input invalid data, by using multiple sessions you can just void that session and not affect the others.
	def createsession(self) :
		"""
		Creates a new session for database transactions.
		:return:
		"""
		return self.sessionmanager()

	def commit(self, session) :
		"""
		Commits the transaction to the database,
		:param session:
		"""
		try :
			session.commit()
		except pymysql.err.InternalError as e :
			logging.warning(e)
			session.rollback()
			# optionally, you can raise a custom error here to track commit failures
			# raise CommitError()
		except SQLAlchemyError as e :
			logging.warning(e)
			session.rollback()
			# optionally, you can raise a custom error here to track commit failures
			# raise CommitError()
		finally :
			# Close the session to free up resources
			session.close()