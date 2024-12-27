from . import users, perms, weather, sessions, blob, bugs, book, settings, notification, apikeys, inventory, datafeed
from pymongo import MongoClient
from application.types import blob_storage
from application.exceptions import BadUserNameError, UserExistsError


def init_db(data_db_url: str = 'localhost', blob_path: str = None) -> None:
	"""
	Initialize the database connections and set up the necessary collections.

	This function connects to the MongoDB instance specified by `data_db_url` and
	initializes various collections used by the application. It also sets the path
	for blob storage if provided.

	Args:
		data_db_url (str): The URL of the MongoDB instance to connect to. Defaults to 'localhost'.
		blob_path (str, optional): The path for blob storage. Defaults to None.

	Returns:
		None
	"""
	client = MongoClient(data_db_url)
	blob_storage.blob_path = blob_path

	users.db = client.skrunk.users
	users.top_level_db = client.skrunk

	apikeys.db = client.skrunk.api_keys

	perms.apikeydb = apikeys.db

	settings.db = client.skrunk.settings

	sessions.db = client.skrunk.user_sessions

	blob.db = client.skrunk.blob
	blob.init()

	bugs.db = client.skrunk.bug_reports
	book.db = client.skrunk.books
	book.init()

	notification.db = client.skrunk
	inventory.db = client.skrunk

	weather.db = client.skrunk

	datafeed.db = client.skrunk


def setup_db() -> None:
	"""
	Sets up the database by performing the following actions:

	1. Attempts to create a temporary admin user.
	   If the user creation fails, the exception is caught and ignored.

	2. Creates necessary indexes for the database to function properly:
	   - An index on the 'expires' field in the sessions collection with an expiration time of 1 second.
	   - An index on the 'title' field in the book collection.
	"""
	try:
		users.create_user('admin', '', admin=True, ephemeral=True)
	except BadUserNameError | UserExistsError:
		pass

	# Create all indexes that are needed for the db to function properly
	sessions.db.create_index([('expires', 1)], expireAfterSeconds=1)
	book.db.create_index([('title', 1)])
