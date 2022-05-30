import application.exceptions as exceptions
from pymongo import MongoClient

__mongo_url = 'mongodb://192.168.1.184:27017/'

def get_user_data(username: str) -> dict:
	global __mongo_url

	db = MongoClient(__mongo_url)
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(f'User "{username}" does not exist.')

def update_user_token(username: str, login_token: str) -> None:
	global __mongo_url

	db = MongoClient(__mongo_url)
	db.data.users.update_one({'username': username}, {'$set': {'login_token': login_token}})
