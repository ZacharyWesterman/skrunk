import ariadne
from flask import Flask, Response, request, jsonify

from ariadne.constants import PLAYGROUND_HTML
from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation
from .tokens import *
from .db.users import authenticate
from .scalars import scalars
from .db import init_db, blob

import mimetypes

import re
import os

def init(*, no_auth = False, blob_path = None, data_db_url = '', weather_db_url = ''):
	init_db(data_db_url, weather_db_url)

	application = Flask(__name__)

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = make_federated_schema(type_defs, [query, mutation] + scalars)

	def read_file_data(path: str):
		with open(path, 'rb') as fp:
			mime = mimetypes.guess_type(path)
			if mime:
				return Response(fp.read(), 200, mimetype=mime[0])
			else:
				return fp.read(), 200

	def authorized():
		if no_auth:
			print('NO-AUTH: Auth set to True')
			return True

		token = get_request_token()
		if token is None:
			return False

		return token_is_valid(token)

	@application.route('/auth/verify', methods=['POST', 'GET'])
	def verify_token():
		data = request.get_json()

		if 'token' not in data:
			return '{"valid":false}', 200

		token = data['token'].split(' ')
		if len(token) < 2:
			return '{"error":"Invalid Token"}', 400

		return jsonify({'valid': token_is_valid(token[1])}), 200

	@application.route('/auth', methods=['POST', 'GET'])
	def auth_user():
		data = request.get_json()

		#Refresh user login token
		if 'token' in data:
			token = data['token'].split(' ')
			if len(token) < 2:
				return '{"error":"Invalid Token"}', 400

			if not token_is_valid(token[1]):
				return '{"error":"Expired Token"}', 400

			username = decode_user_token(token[1])['username']
			login_token = create_user_token(username)
			return f'{{"token":"Bearer {login_token}"}}', 200

		if 'username' not in data or 'password' not in data:
			return '{"error":"Authentication failed"}', 400

		try:
			login_token = authenticate(data['username'], data['password'])
			return f'{{"token":"{login_token}"}}', 200
		except exceptions.ClientError as e:
			return jsonify({'error': str(e)}), 403


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
		return site('html/index.html')

	@application.route('/<path:path>', methods=['GET'])
	def site(path):
		# Allow only specific files in site/, as other files may have "sensitive" data.
		allowed = [
			'html/index.html',
			'html/login.html',
			'js/page/index.js',
			'js/api.js',
			'js/doT.js',
			'js/fields.js',
		]
		jsfields = re.match(r'js/fields/[\w-]+\.js', path)
		styles = re.match(r'css/[\w-]+\.css', path)
		if not authorized() and path not in allowed and not jsfields and not styles:
			return '', 403

		i = path.rindex('.')
		if i > -1:
			ext = path[i+1::]
		else:
			ext = ''

		if ext in ['js', 'css', 'html', 'dot']:
			try:
				return read_file_data(f'site/{path}')
			except FileNotFoundError as e:
				return '', 404
		else:
			if authorized():
				return '', 404
			else:
				return '', 403

	@application.after_request
	def after_request(response):
		response.headers.add('Accept-Ranges', 'bytes')
		return response

	def get_chunk(full_path: str, byte1: int, byte2: int):
		file_size = os.stat(full_path).st_size
		start = 0

		if byte1 < file_size:
			start = byte1
		if byte2:
			length = byte2 + 1 - byte1
		else:
			length = file_size - start

		with open(full_path, 'rb') as fp:
			fp.seek(start)
			chunk = fp.read(length)

		return chunk, start, length, file_size

	@application.route('/blob/<path:path>', methods=['GET'])
	def blob_stream(path: str):
		if not authorized():
			return '', 403

		if blob_path is None:
			return 'No blob data path specified in server setup.', 404

		range_header = request.headers.get('Range')
		byte1, byte2 = 0, None
		if range_header:
			match = re.search(r'(\d+)-(\d*)', range_header)
			groups = match.groups()

			if groups[0]:
				byte1 = int(groups[0])
			if groups[1]:
				byte2 = int(groups[1])

		full_path = f'{blob_path}/{path}'
		try:
			chunk, start, length, file_size = get_chunk(full_path, byte1, byte2)
			mime = mimetypes.guess_type(path)

			resp = Response(chunk, 206, mimetype=mime[0], content_type=mime[0], direct_passthrough=True)
			resp.headers.add('Content-Range', f'bytes {start}-{start+length-1}/{file_size}')
			return resp
		except FileNotFoundError as e:
			return '', 404

	@application.route('/favicon.ico', methods=['GET'])
	def favicon():
		return read_file_data('data/favicon.ico')

	@application.route('/background.svg', methods=['GET'])
	def background_image():
		return read_file_data('data/background.svg')

	@application.route('/upload', methods=['POST'])
	def upload_file():
		if not authorized():
			return '', 403

		if blob_path is None:
			return 'No blob data path specified in server setup.', 404

		f = request.files.get('file')
		if f is None:
			return 'No file given.', 400

		id, ext = blob.create_blob(blob_path, f.filename)
		f.save(f'{blob_path}/{id}.{ext}')

		return str(id), 200

	return application
