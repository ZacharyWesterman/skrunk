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

def authenticate(username: str, password: str) -> str:
	userdata = get_user_data(username)

	if not bcrypt.checkpw(password.encode(), userdata.get('password').encode()):
		raise exceptions.AuthenticationError(f'Authentication failed')

	login_token = create_user_token(username)

	return login_token

from application.tokens import create_user_token
