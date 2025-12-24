from data.env.loader import load_environment
# This loads before the database, so the test database environment variables are used.
load_environment('.env.test', override=True)

import unittest

from database.database import Users, create_bot_database, drop_bot_database
from database.transactions.UserTransactions import UserTransactions

# Why should you test your code?
# Testing your code ensures that it works as expected and helps catch bugs early in the development process
# Whenever you make a change to your codebase, running tests can help verify that existing functionality remains intact
# You can ensure that your important functions, such as writing to the database, are working correctly.
# Tests are generally only recommended for local functions, so avoid testing external APIs or libraries unless absolutely necessary.

class TestUserTransactions(unittest.TestCase) :
	def setUp(self) :
		create_bot_database()
		self.ut = UserTransactions()
		self.uid = 123456789012345678

	def tearDown(self) :
		drop_bot_database()

	def test_add_user_empty(self) :

		# Test adding a user that does not exist
		result = self.ut.create_user(self.uid)
		self.assertIsInstance(result, Users)
		self.assertEqual(result.id, self.uid)
		# Now we test a negative scenario, it should still return the user even if they exist
		result = self.ut.create_user(self.uid)
		self.assertIsInstance(result, Users)
		self.assertEqual(result.id, self.uid)

	def test_user_exists(self) :
		# Test user does not exist
		exists = self.ut.user_exists(self.uid)
		self.assertFalse(exists)
		# Add user
		self.ut.create_user(self.uid)
		# Test user exists
		exists = self.ut.user_exists(self.uid)
		self.assertTrue(exists)

	def test_update_user(self) :
		# Test updating a user that does not exist
		result = self.ut.update_user(self.uid, messages=10, xp=100)
		self.assertIsNone(result)
		# Add user
		self.ut.create_user(self.uid)
		# Test updating the user
		result = self.ut.update_user(self.uid, messages=10, xp=100)
		self.assertIsInstance(result, Users)
		self.assertEqual(result.messages, 10)
		self.assertEqual(result.xp, 100)

	def test_delete_user(self) :
		# Test deleting a user that does not exist
		result = self.ut.delete_user(self.uid)
		self.assertFalse(result)
		# Add user
		self.ut.create_user(self.uid)
		# Test deleting the user
		result = self.ut.delete_user(self.uid)
		self.assertTrue(result)
		# Verify user is deleted
		exists = self.ut.user_exists(self.uid)
		self.assertFalse(exists)

	def test_get_user(self) :
		# Test getting a user that does not exist
		result = self.ut.get_user(self.uid)
		self.assertIsNone(result)
		# Add user
		self.ut.create_user(self.uid)
		# Test getting the user
		result = self.ut.get_user(self.uid)
		self.assertIsInstance(result, Users)
		self.assertEqual(result.id, self.uid)



