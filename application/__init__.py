import ariadne
from flask import Flask, Response, request, jsonify

from ariadne.constants import PLAYGROUND_HTML
from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation
from .tokens import decode_user_token
from .db.users import authenticate

import mimetypes

def init():
	application = Flask(__name__)

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = make_federated_schema(type_defs, [query, mutation])

	def authorized():
		if 'Authorization' not in request.headers:
			return False

		try:
			decode_user_token(request.headers['Authorization'])
			return True
		except Exception as e:
			print(e)
			return False

	@application.route('/auth', methods=['POST', 'GET'])
	def auth_user():
		data = request.get_json()

		if 'username' not in data or 'password' not in data:
			return '{"error":"Authentication failed"}', 400

		try:
			login_token = authenticate(data['username'], data['password'])
			return f'{{"token":"{login_token}"}}', 200
		except Exception as e:
			return jsonify({'error': str(e)}), 400


	@application.route('/api', methods=['POST'])
	def graphql():
		if not authorized():
			return '', 403

		data = request.get_json()
		success, result = ariadne.graphql_sync(schema, data, context_value=request, debug=application.config.get('DEBUG'))

		if not success:
			result_code = 400
		elif result.get('errors'):
			result_code = 500
		else:
			result_code = 200

		return jsonify(result), result_code

	@application.route('/', methods=['GET'])
	def main_page():
		if authorized():
			return site('html/index.html')
		else:
			return site('html/login.html')

	@application.route('/<path:path>', methods=['GET'])
	def site(path):
		# Allow anything in site/, those will have no sensitive data anyway.
		# if path not in ['html/login.html', 'js/api.js'] and not authorized():
		# 	return '', 403

		try:
			with open(f'site/{path}', 'r') as fp:
				mime = mimetypes.guess_type(path)
				if mime:
					return Response(fp.read(), 200, mimetype=mime[0])
				else:
					return fp.read(), 200
		except Exception as e:
			return '', 404

	return application
