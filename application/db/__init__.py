from . import users, perms, weather, sessions, blob, bugs, book, settings, notification, apikeys, inventory, datafeed
from pymongo import MongoClient

def init_db(data_db_url: str = 'localhost', blob_path: str = None) -> None:
	client = MongoClient(data_db_url)

	users.db = client.skrunk.users
	users.top_level_db = client.skrunk

	apikeys.db = client.skrunk.api_keys

	perms.apikeydb = apikeys.db

	settings.db = client.skrunk.settings

	sessions.db = client.skrunk.user_sessions

	blob.db = client.skrunk.blob
	blob.blob_path = blob_path
	blob.init()

	bugs.db = client.skrunk.bug_reports
	book.db = client.skrunk.books
	book.init()

	notification.db = client.skrunk
	inventory.db = client.skrunk

	weather.db = client.skrunk

	datafeed.db = client.skrunk

def setup_db() -> None:
	try:
		users.create_user('admin', '', admin = True, ephemeral = True)
	except:
		pass

	#Create all indexes that are needed for the db to function properly
	sessions.db.create_index([('expires', 1)], expireAfterSeconds = 1)
	book.db.create_index([('title', 1)])
