import application.exceptions as exceptions
from pymongo import MongoClient

import bcrypt

__mongo_url = 'mongodb://192.168.1.184:27017/'

def get_user_data(username: str) -> dict:
	global __mongo_url

	db = MongoClient(__mongo_url)
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(f'User "{username}" does not exist.')

def create_user(username: str, password: str) -> None:
	global __mongo_url

	if len(username) == 0:
		raise exceptions.InvalidUsername(f'Invalid username.')

	db = MongoClient(__mongo_url)
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		raise exceptions.UserExistsError(f'User "{username}" already exists.')

	db.data.users.insert_one({
		'username': username,
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
	})


def authenticate(username: str, password: str) -> str:
	userdata = get_user_data(username)

	if not bcrypt.checkpw(password.encode(), userdata.get('password')):
		raise exceptions.AuthenticationError(f'Authentication failed')

	login_token = create_user_token(username)

	return login_token

from application.tokens import create_user_token
