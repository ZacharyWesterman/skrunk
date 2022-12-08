from cryptography.hazmat.primitives import serialization
import jwt, os
from datetime import datetime, timedelta

from .db.sessions import start_session, valid_session

__private_key = serialization.load_ssh_private_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa', 'r').read().encode(), password=b'')
__public_key = serialization.load_ssh_public_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa.pub', 'r').read().encode())

def create_user_token(username: str) -> str:
	global __private_key
	token = jwt.encode(
		payload = {
			'username': username,
		},
		key = __private_key,
		algorithm = 'RS256'
	)
	start_session(token, username)
	return token

def decode_user_token(token: str) -> dict:
	global __public_key
	return jwt.decode(
		token,
		key = __public_key,
		algorithms = ['RS256']
	)

def token_is_valid(token: str) -> bool:
	return valid_session(token)
