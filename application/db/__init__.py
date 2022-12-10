from . import users, perms, weather, sessions, blob
from pymongo import MongoClient

def init_db(data_db_url, weather_db_url, blob_path):
	users.db = MongoClient(data_db_url)
	perms.db = users.db
	sessions.db = users.db
	blob.db = users.db
	blob.blob_path = blob_path

	weather.db = MongoClient(weather_db_url)
