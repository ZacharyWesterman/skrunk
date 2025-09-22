"""application.routes.auth"""

from typing import Any

from flask import Response, jsonify, request

from application import exceptions, tokens
from application.db.notification import send
from application.db.users import (authenticate, create_reset_code,
                                  reset_user_password)

application: Any = None


def authorized() -> bool:
	"""
	Check if the user is authorized to access the application.

	Returns:
		bool: True if the user is authorized, False otherwise.
	"""

	if not application.is_initialized:
		print('INIT: No users exist, giving access for database setup!', flush=True)
		return True

	if application.no_auth:
		print('NO-AUTH: User authentication disabled!', flush=True)
		return True

	token = tokens.get_request_token()
	if token is None:
		return False

	return tokens.token_is_valid(token)


def auth_user() -> Response:
	"""
	Authenticate a user and return a login token.

	Returns:
		Response: A Flask Response object containing the login token or an error message.
	"""

	if not application.is_initialized:
		return jsonify({'token': tokens.create_user_token('admin')})

	data = request.get_json()

	# Refresh user login token
	if 'token' in data:
		token = data['token'].split(' ')
		if len(token) < 2:
			return Response('{"error":"Invalid Token"}', 400)

		if not tokens.token_is_valid(token[1]):
			return Response('{"error":"Expired Token"}', 400)

		username = (
			data['username']
			if 'username' in data
			else tokens.decode_user_token(token[1])['username']
		)
		login_token = tokens.create_user_token(username)
		return jsonify({'token': f'Bearer {login_token}'})

	if 'username' not in data or 'password' not in data:
		return Response('{"error":"Authentication failed"}', 400)

	try:
		login_token = authenticate(data['username'], data['password'])
		return jsonify({'token': login_token})
	except exceptions.ClientError as e:
		return jsonify({'error': str(e)})


def verify_token() -> Response:
	"""
	Verify the validity of a user token.

	Returns:
		Response: A Flask Response object indicating whether the token is valid or not.
	"""

	if not application.is_initialized:
		return jsonify({'valid': True})

	data = request.get_json()

	if 'token' not in data:
		return Response('{"valid":false}', 200)

	token = data['token'].split(' ')
	if len(token) < 2:
		return Response('{"error":"Invalid Token"}', 400)

	return jsonify({'valid': tokens.token_is_valid(token[1])})


def request_reset_code() -> Response:
	"""
	Request a notification containing a password reset code be sent to the user.

	Returns:
		Response: A Flask Response object indicating success or failure of the request.
	"""

	if not application.is_initialized:
		return Response("{'error': 'Application not initialized'}", 200)

	data = request.get_json()

	if 'username' not in data:
		return Response("{'error': 'Invalid request'}", 200)

	username = data['username']

	try:
		code = create_reset_code(username)
		send(
			f'{code} is your password reset code.',
			(
				'A password reset was requested for your account. ' +
				'If you did not make this request, you can ignore this message. ' +
				f'Otherwise, use the following code to reset your password: {code}'
			),
			username,
			category='password-reset',
		)
	except exceptions.ClientError as e:
		return jsonify({'error': str(e)})

	# DO NOT EVER RETURN THE CODE FROM HERE.
	# It could be used by an attacker to reset the password
	# without access to the user's account!
	return jsonify({'success': True})


def reset_password() -> Response:
	"""
	Reset a user's password using a reset code.

	Returns:
		Response: A Flask Response object indicating success or failure of the password reset.
	"""

	if not application.is_initialized:
		return Response("{'error': 'Application not initialized'}", 200)

	data = request.get_json()

	if any(key not in data for key in ['username', 'code', 'new_password']):
		return Response("{'error': 'Invalid request'}", 200)

	username = data['username']
	code = data['code']
	new_password = data['new_password']

	try:
		reset_user_password(username, code, new_password)
	except exceptions.ClientError as e:
		return jsonify({'error': str(e)})

	return jsonify({'success': True})
