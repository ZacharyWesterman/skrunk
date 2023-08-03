from . import users, perms, weather, sessions, blob, bugs, book, settings
from pymongo import MongoClient

def init_db(data_db_url: str = 'localhost', weather_db_url: str = 'localhost', blob_path: str = None) -> None:
	data_client = MongoClient(data_db_url)
	weather_client = MongoClient(weather_db_url)

	users.db = data_client.data.users
	perms.db = data_client.data.users
	settings.db = data_client.data.settings

	sessions.db = data_client.data.user_sessions

	blob.db = data_client.data.blob
	blob.blob_path = blob_path

	bugs.db = data_client.data.bug_reports
	book.db = data_client.data.books

	weather.db = weather_client

def setup_db() -> None:
	try:
		users.create_user('admin', '', admin = True, ephemeral = True)
	except:
		pass

	#Create all indexes that are needed for the db to function properly
	sessions.db.create_index([('expires', 1)], expireAfterSeconds = 1)
	book.db.create_index([('title', 1)])