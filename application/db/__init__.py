from . import users, perms, weather, sessions, blob
from pymongo import MongoClient

def init_db(data_db_url, weather_db_url):
	users.db = MongoClient(data_db_url)
	perms.db = users.db
	sessions.db = users.db
	blob.db = users.db

	weather.db = MongoClient(weather_db_url)
