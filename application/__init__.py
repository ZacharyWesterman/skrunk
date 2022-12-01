import ariadne
from flask import Flask, Response, request, jsonify

from ariadne.constants import PLAYGROUND_HTML
from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation
from .tokens import decode_user_token
from .db.users import authenticate
from .scalars import scalars

import mimetypes

import re
import os

def init(*, no_auth = False, vid_path = None):
	application = Flask(__name__)

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = make_federated_schema(type_defs, [query, mutation] + scalars)

	def authorized(*, use_cookies=False):
		if no_auth:
			print('NO-AUTH: Auth set to True')
			return True

		if use_cookies:
			token = request.headers['Cookie']
		else:
			if 'Authorization' not in request.headers:
				return False
			token = request.headers['Authorization']

		token = token.split(' ')
		if len(token) < 2:
			return False

		decode_user_token(token[1])
		return True

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
		return site('html/index.html')

	@application.route('/<path:path>', methods=['GET'])
	def site(path):
		# Allow anything in site/, those will have no sensitive data anyway.
		i = path.rindex('.')
		if i > -1:
			ext = path[i+1::]
		else:
			ext = ''

		if ext in ['js', 'css', 'html', 'dot']:
			try:
				with open(f'site/{path}', 'r') as fp:
					mime = mimetypes.guess_type(path)
					if mime:
						return Response(fp.read(), 200, mimetype=mime[0])
					else:
						return fp.read(), 200
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

	@application.route('/video/<path:path>', methods=['GET'])
	def video_stream(path: str):
		if not authorized(use_cookies = True):
			return '', 403

		if vid_path is None:
			return 'No video path specified in server setup.', 404

		range_header = request.headers.get('Range')
		byte1, byte2 = 0, None
		if range_header:
			match = re.search(r'(\d+)-(\d*)', range_header)
			groups = match.groups()

			if groups[0]:
				byte1 = int(groups[0])
			if groups[1]:
				byte2 = int(groups[1])

		full_path = f'{vid_path}/{path}'
		try:
			chunk, start, length, file_size = get_chunk(full_path, byte1, byte2)
			resp = Response(chunk, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)
			resp.headers.add('Content-Range', f'bytes {start}-{start+length-1}/{file_size}')
			return resp
		except FileNotFoundError as e:
			return '', 404

	@application.route('/favicon.ico', methods=['GET'])
	def favicon():
		with open('data/favicon.ico', 'rb') as fp:
			return fp.read(), 200

	return application
