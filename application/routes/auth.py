from flask import jsonify, request, Response
from application import tokens, exceptions
from application.db.users import authenticate

application = None

def authorized() -> bool:
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
	if not application.is_initialized:
		return jsonify({'token': tokens.create_user_token('admin')})

	data = request.get_json()

	#Refresh user login token
	if 'token' in data:
		token = data['token'].split(' ')
		if len(token) < 2:
			return Response('{"error":"Invalid Token"}', 400)

		if not tokens.token_is_valid(token[1]):
			return Response('{"error":"Expired Token"}', 400)

		username = tokens.decode_user_token(token[1])['username']
		login_token = tokens.create_user_token(username)
		return jsonify({'token': f'Bearer {login_token}'})

	if 'username' not in data or 'password' not in data:
		return Response('{"error":"Authentication failed"}', 400)

	try:
		login_token = authenticate(data['username'], data['password'])
		return jsonify({'token': login_token})
	except exceptions.ClientError as e:
		return jsonify({'error': str(e)}), 403

def verify_token() -> Response:
	if not application.is_initialized:
		return jsonify({'valid': True})

	data = request.get_json()

	if 'token' not in data:
		return Response('{"valid":false}', 200)

	token = data['token'].split(' ')
	if len(token) < 2:
		return Response('{"error":"Invalid Token"}', 400)

	return jsonify({'valid': tokens.token_is_valid(token[1])})