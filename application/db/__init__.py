from . import users, creds, weather
from pymongo import MongoClient

def init_db(data_db_url, weather_db_url):
	users.db = MongoClient(data_db_url)
	creds.db = users.db

	weather.db = MongoClient(weather_db_url)
