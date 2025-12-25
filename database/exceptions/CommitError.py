# To make a class an exception, you need to subclass the built-in Exception class.
class CommitError(Exception) :
	"""the commit failed, and the session was rolled back"""
	# To set the error of an exception, we override the init function
	def __init__(self, message="Commiting the data to the database failed and has been rolled back; please try again.") :
		self.message = message
		super().__init__(self.message)
