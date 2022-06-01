import application.exceptions as exceptions
from pymongo import MongoClient

from cryptography.hazmat.primitives import serialization
import jwt, os

__mongo_url = 'mongodb://192.168.1.184:27017/'
__private_key = serialization.load_ssh_private_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa', 'r').read().encode(), password=b'')
__public_key = serialization.load_ssh_public_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa.pub', 'r').read().encode())

def get_user_data(username: str) -> dict:
	global __mongo_url

	db = MongoClient(__mongo_url)
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(f'User "{username}" does not exist.')

def create_user_token(username: str) -> None:
	global __private_key
	return jwt.encode(
		payload = {'username': username},
		key = __private_key,
		algorithm = 'RS256'
	)

def decode_user_token(token: str) -> dict:
	global __public_key
	return jwt.decode(
		token,
		key = __public_key,
		algorithm = 'RS256'
	)
