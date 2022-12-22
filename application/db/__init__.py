from . import users, perms, weather, sessions, blob
from pymongo import MongoClient

def init_db(data_db_url, weather_db_url, blob_path):
	data_db = MongoClient(data_db_url)
	users.db = data_db
	perms.db = data_db
	sessions.db = data_db
	blob.db = data_db.data.blob
	blob.blob_path = blob_path

	weather.db = MongoClient(weather_db_url)
