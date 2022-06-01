import ariadne
from flask import Flask, Response, request, jsonify

from ariadne.constants import PLAYGROUND_HTML
from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation

import mimetypes

def init():
	application = Flask(__name__)

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = make_federated_schema(type_defs, [query, mutation])

	@application.route('/api', methods=['POST'])
	def graphql():
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
		return site('html/login.html')

	@application.route('/<path:path>', methods=['GET'])
	def site(path):
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
