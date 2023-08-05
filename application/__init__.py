import ariadne
from flask import Flask, Response, request, jsonify

from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation
from .tokens import *
from .db.users import count_users
from .scalars import scalars
from .db import init_db, blob, setup_db
from . import routes

import mimetypes
import requests
import random

import json
import re
import os

def init(*, no_auth = False, blob_path = None, data_db_url = '', weather_db_url = ''):
	init_db(data_db_url, weather_db_url, blob_path)

	application = Flask(__name__)
	application.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000 #5GB file size limit for uploads

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = make_federated_schema(type_defs, [query, mutation] + scalars)

	application.is_initialized = count_users() > 0
	application.no_auth = no_auth

	#Create temporary admin user if server hasn't been set up yet
	if not application.is_initialized:
		setup_db()

	routes.init(application)

	def read_file_data(path: str):
		try:
			with open(path, 'rb') as fp:
				mime = mimetypes.guess_type(path)
				if mime:
					return Response(fp.read(), 200, mimetype=mime[0])
				else:
					return fp.read(), 200
		except FileNotFoundError:
			return '', 404

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

	@application.route('/xkcd', methods=['GET'])
	def random_xkcd():
		comic_num = random.randint(0, 600)
		response = requests.get(f'https://xkcd.com/{comic_num}/info.0.json')

		return response.text, response.status_code

	@application.route('/<path:path>', methods=['GET'])
	def site(path):
		# Allow only specific files in site/ to be accessed without auth, as other files may have "sensitive" data.
		allowed = [
			'html/index.html',
			'html/login.html',
			'js/page/login.js',
			'js/api.js',
			'js/doT.js',
			'js/fields.js',
			'js/navigate.js',
			'js/runtime_errors.js',
		]
		jsfields = re.match(r'js/fields/[\w-]+\.js', path)
		styles = re.match(r'css/[\w-]+\.css', path)
		if not authorized() and path not in allowed and not jsfields and not styles:
			return '', 403

		if USER_COUNT == 0 and path == 'html/login.html':
			with open(f'site/{path}') as fp:
				return fp.read().replace('Authentication Required', '<b class="error">This server has not been set up.<br><br>Login as user "admin" (any password) and create at least one user.<br><br>Then restart the server, and (optionally) delete the admin user.</b>'), 200

		i = path.rindex('.')
		if i > -1:
			ext = path[i+1::]
		else:
			ext = ''

		if ext in ['js', 'css', 'html', 'dot', 'json']:
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

		length = min(length, 1024*1024*5) #Max chunk size is 5MiB

		with open(full_path, 'rb') as fp:
			fp.seek(start)
			chunk = fp.read(length)

		return chunk, start, length, file_size

	@application.route('/blob/<path:path>', methods=['GET'])
	def blob_stream(path: str):
		# if not authorized():
		# 	return '', 403

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

		full_path = blob.path(path)
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

	@application.route('/<path:path>.svg', methods=['GET'])
	def get_image(path: str):
		return read_file_data(f'data/{path}.svg')

	@application.route('/download/<path:path>', methods=['GET'])
	def download_file(path: str):
		if not authorized():
			return '', 403

		if blob_path is None:
			return 'No blob data path specified in server setup.', 404

		full_path = blob.path(path)
		return read_file_data(full_path)

	@application.route('/preview/<path:path>', methods=['GET'])
	def download_preview(path: str):
		if not authorized():
			return '', 403

		if blob_path is None:
			return 'No blob data path specified in server setup.', 404

		full_path = blob.preview(path)
		return read_file_data(full_path)

	@application.route('/upload', methods=['POST'])
	def upload_file():
		if not authorized():
			return '', 403

		if blob_path is None:
			return 'No blob data path specified in server setup.', 404

		auto_unzip = request.form['unzip'] == 'true'
		tag_list = json.loads(request.form['tags'])
		uploaded_blobs = blob.save_blob_data(request.files['file'], auto_unzip, tag_list)

		return jsonify(uploaded_blobs), 200

	return application
