import application.exceptions as exceptions
from pymongo import MongoClient

def get_user_data(username: str) -> dict:
	db = MongoClient('mongodb://192.168.1.184:27017/')
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(f'User "{username}" does not exist.')
