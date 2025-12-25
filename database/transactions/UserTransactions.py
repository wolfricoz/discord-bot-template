"""This is an example of how to make a database transaction class for user transactions."""
from sqlalchemy import Select, exists

from database.database import Users
from database.transactions.DatabaseTransactions import DatabaseTransactions

# We input the DatabaseTransactions as the base class to inherit the database connection and basic functions, this allows us to reuse the base class without having to repeat ourselves.
# we will be making a simple crud (create, read, update, delete) transaction class for the Users table.
class UserTransactions(DatabaseTransactions):
	# We define the table we will be using for this transaction class.
	table = Users

	# You can find the database schema in database/database.py, we will be using the Users table for this example.

	# This function gets the user from the database based on their user_id, you can also name it a simple 'get' but I personally prefer to be more descriptive because:
	# - 'get' is used in many places and can be confusing when reading code later on.
	# - it explains a little more about what the function does.
	def get_user(self, user_id: int) -> Users :
		"""We create a new session using the createsession function from the base class."""
		with self.createsession() as session:
			# We use the orm 'scalar' function to get a single result from the database, we use the Select function to create a select statement for the Users table where the id matches the user_id passed to the function.
			# for easy transactions I tend to prefer the ORM style queries because if you change database backends later on you don't have to rewrite all your queries.
			# However if you are doing complex queries you want to use raw SQL for the control and performance.
			return session.scalar(Select(self.table).where(self.table.id == user_id))

	def get_all_users(self) -> Users :
		"""like the get_user function we create a new session and use the Select function to get all users from the Users table."""
		with self.createsession() as session:
			# This time we use scalars (this returns multiple results) and use the 'all' function to get all results as a list.
			return session.scalars(Select(self.table)).all()

	def create_user(self, user_id: int) -> Users :
		"""This function creates a new user in the database. """
		if self.user_exists(user_id) :
			# If the user already exists we return the existing user instead of creating a new one.
			return self.get_user(user_id)

		with self.createsession() as session:
			# We create a new Users object with the user_id passed to the function. Because the other fields have defaults we don't need to fill them right now.
			new_user = self.table(id=user_id)
			# We add the new user to the session.
			session.add(new_user)
			# We commit the session to save the changes to the database.
			self.commit(session)
			# We return the new user object. Because we used expire_on_commit=False in the sessionmaker, we can still access the attributes of the new_user object after the commit.
			return new_user

	def user_exists(self, user_id: int) -> bool :
		"""This function checks if a user exists in the database."""
		with self.createsession() as session:
			# We use the query function to get the user from the database. by using the 'exists' function we can check if the user exists without having to retrieve the entire user object.
			return session.scalar(Select(exists().where(self.table.id == user_id)))

	# You could also do this with a dictionary but for this example we will use individual parameters because it's easier to read, especially for beginners.
	def update_user(self, userid:int ,  messages: int = None, xp:int = None) -> Users | None :
		"""This is an example function to update a user in the database, you can add parameters as needed to update specific fields."""

		# We create a dictionary of fields to update, this allows us to easily loop through the fields and update them if they are not None.
		fields = {
			"messages": messages,
			"xp": xp,
		}
		with self.createsession() as session:
			user = self.get_user(userid)
			if not user :
				# If you want, you could also just make the user here, or throw an exception, but for this example we will just return None.
				return None
			for field, value in fields.items():
				if value is not None:
					# we use the python built-in setattr function to set the attribute of the user object to the new value.
					setattr(user, field, value)
			# We add the user to the session and commit the changes.
			session.add(user)
			self.commit(session)
			return user

	def delete_user(self, user_id: int) -> bool :
		"""This function deletes a user from the database."""
		with self.createsession() as session:
			user = self.get_user(user_id)
			if not user :
				return False
			# Delete the user from the database.
			session.delete(user)
			self.commit(session)
			return True








