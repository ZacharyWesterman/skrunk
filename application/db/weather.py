import application.exceptions as exceptions
from pymongo import MongoClient

import bcrypt

__mongo_url = 'mongodb://192.168.1.184:27017/'
db = MongoClient(__mongo_url)

def get_users() -> list:
	global db
	users = [ user for user in db.weather.users.find({'exclude': False}) ]

	return sorted(users, key = lambda elem: elem['_id'])
