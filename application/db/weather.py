import application.exceptions as exceptions
from pymongo import MongoClient

import bcrypt

__mongo_url = 'mongodb://192.168.1.184:27017/'
db = MongoClient(__mongo_url)

def get_users() -> list:
	global db
	users = [ user for user in db.weather.users.find({'exclude': False}) ]
	for i in users:
		i['username'] = i['_id']

	return sorted(users, key = lambda elem: elem['username'])

def create_user(user_data: dict) -> None:
	global db

	userdata = db.weather.users.find_one({'_id': user_data['username']})

	if userdata:
		raise exceptions.UserExistsError(f'User "{username}" already exists.')
	else:
		userdata = {
			'_id': user_data['username'],
			'lat': user_data['lat'],
			'lon': user_data['lon'],
			'phone': user_data['phone'],
			'last_sent': None,
			'exclude': False,
		}
		db.weather.users.insert_one(userdata)

def delete_user(username: str) -> None:
	global db

	userdata = db.weather.users.find_one({'_id': username})

	if userdata:
		db.weather.users.delete_one({'_id': username})
	else:
		raise exceptions.UserDoesNotExistError(f'User "{username}" does not exist.')
