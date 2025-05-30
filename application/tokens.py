"""
This module handles JWT token creation, decoding, and validation for user sessions and API keys.
"""

import os
import random
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from flask import request

from .db.apikeys import valid_api_key
from .db.sessions import start_session, valid_session
from .exceptions import InvalidJWTError

__private_key: Any = None
__public_key: Any = None


def init() -> None:
	"""
	Initialize the JWT token system by loading the private and public keys.
	"""

	global __private_key, __public_key

	with open(os.environ['HOME'] + '/.ssh/id_rsa', 'r', encoding='utf8') as fp:
		__private_key = serialization.load_ssh_private_key(fp.read().encode(), password=b'')
	with open(os.environ['HOME'] + '/.ssh/id_rsa.pub', 'r', encoding='utf8') as fp:
		__public_key = serialization.load_ssh_public_key(fp.read().encode())


__MAX_INT = 2**32 - 1


def create_user_token(username: str) -> str:
	"""
	Generate a JWT token for a given username and start a session.

	This function creates a JWT token using the provided username and a randomly generated token ID.
	The token is signed using a private key and the RS256 algorithm. After generating the token,
	it starts a session with the token and username.

	Args:
		username (str): The username for which the token is being created.

	Returns:
		str: The generated JWT token.
	"""
	token = jwt.encode(
		payload={
			'username': username,
			'token_id': random.randint(0, __MAX_INT),
		},
		key=__private_key,
		algorithm='RS256'
	)
	start_session(token, username)
	return token


def decode_user_token(token: str) -> dict:
	"""
	Decodes a JWT token using a global public key.

	Args:
		token (str): The JWT token to decode.

	Returns:
		dict: The decoded token payload.

	Raises:
		InvalidJWTError: If the token is expired or invalid.
	"""
	try:
		return jwt.decode(
			token,
			key=__public_key,
			algorithms=['RS256']
		)
	except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
		raise InvalidJWTError from e


def token_is_valid(token: str) -> bool:
	"""
	Check if the provided token is valid.

	This function checks the validity of a token by verifying if it is either a valid session token
	or a valid API key.

	Args:
		token (str): The token to be validated.

	Returns:
		bool: True if the token is valid, False otherwise.
	"""
	return valid_session(token) or valid_api_key(token)


def get_request_token() -> str | None:
	"""
	Extracts the authorization token from the request headers.

	The function checks for the 'Authorization' header first. If not found,
	it looks for the 'Cookie' header and attempts to decode it to find the
	'Authorization' token. If neither is found, it returns None.

	Returns:
		str: The extracted token if present and valid, otherwise None.
	"""
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
	"""
	Decodes a string of cookies into a dictionary.

	Args:
		cookies (str): A string containing cookies in the format 'key1=value1; key2=value2; ...'.

	Returns:
		dict: A dictionary where the keys are cookie names and the values are cookie values.
	"""
	output = {}
	for i in cookies.split(';'):
		cookie = i.split('=')
		if len(cookie) > 1:
			key, value = cookie[0].strip(), cookie[1].strip()
			if key != '':
				output[key] = value
	return output
