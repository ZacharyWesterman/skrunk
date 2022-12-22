from . import users, perms, weather, sessions, blob
from pymongo import MongoClient

def init_db(data_db_url, weather_db_url, blob_path):
	data_client = MongoClient(data_db_url)
	weather_client = MongoClient(weather_db_url)

	users.db = data_client.data.users
	perms.db = data_client.data.users

	sessions.db = data_client.data.user_sessions

	blob.db = data_client.data.blob
	blob.blob_path = blob_path

	weather.db = weather_client
