from cryptography.hazmat.primitives import serialization
import jwt, os
from datetime import datetime, timedelta

__private_key = serialization.load_ssh_private_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa', 'r').read().encode(), password=b'')
__public_key = serialization.load_ssh_public_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa.pub', 'r').read().encode())

def create_user_token(username: str) -> None:
	global __private_key
	return jwt.encode(
		payload = {
			'username': username,
			'issued': int(datetime.now().timestamp())
		},
		key = __private_key,
		algorithm = 'RS256'
	)

def decode_user_token(token: str) -> dict:
	global __public_key
	return jwt.decode(
		token,
		key = __public_key,
		algorithms = ['RS256']
	)

def token_is_valid(token: str) -> bool:
	payload = decode_user_token(token)
	issued = datetime.fromtimestamp(payload['issued'])

	# Token is only valid for a limited time.
	expires = issued + timedelta(days = 1)
	if expires < datetime.now():
		return False

	return True
