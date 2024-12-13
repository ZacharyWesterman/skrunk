from cryptography.hazmat.primitives import serialization
import jwt
import os
from flask import request
import random

from .db.sessions import start_session, valid_session
from .db.apikeys import valid_api_key

__private_key = serialization.load_ssh_private_key(open(os.environ['HOME'] + '/.ssh/id_rsa', 'r').read().encode(), password=b'')
__public_key = serialization.load_ssh_public_key(open(os.environ['HOME'] + '/.ssh/id_rsa.pub', 'r').read().encode())

__max_int = 2**32 - 1


def create_user_token(username: str) -> str:
	global __private_key, __max_int
	token = jwt.encode(
		payload={
			'username': username,
			'token_id': random.randint(0, __max_int),
		},
		key=__private_key,
		algorithm='RS256'
	)
	start_session(token, username)
	return token


def decode_user_token(token: str) -> dict:
	global __public_key
	return jwt.decode(
		token,
		key=__public_key,
		algorithms=['RS256']
	)


def token_is_valid(token: str) -> bool:
	return valid_session(token) or valid_api_key(token)


def get_request_token() -> str:
	if 'Authorization' in request.headers:
		token = request.headers['Authorization']
	elif 'Cookie' in request.headers:
		token = decode_cookies(request.headers['Cookie']).get('Authorization', '')
	else:
		return None

	token = token.split(' ')
	if len(token) < 2:
		return None

	return token[1]


def decode_cookies(cookies: str) -> dict:
	output = {}
	for i in cookies.split(';'):
		cookie = i.split('=')
		if len(cookie) > 1:
			key, value = cookie[0].strip(), cookie[1].strip()
			if key != '':
				output[key] = value
	return output
