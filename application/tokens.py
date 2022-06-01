from cryptography.hazmat.primitives import serialization
import jwt, os

__private_key = serialization.load_ssh_private_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa', 'r').read().encode(), password=b'')
__public_key = serialization.load_ssh_public_key(open('/home/'+os.environ['USER']+'/.ssh/id_rsa.pub', 'r').read().encode())

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
		algorithms = ['RS256']
	)
