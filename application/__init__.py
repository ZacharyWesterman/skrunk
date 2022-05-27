import ariadne
from flask import Flask, request, jsonify

from ariadne.constants import PLAYGROUND_HTML
from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation

def init():
	application = Flask(__name__)

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = make_federated_schema(type_defs, [query, mutation])

	@application.route('/playground', methods=['POST'])
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

	@application.route('/playground', methods=['GET'])
	def playground():
		return PLAYGROUND_HTML

	return application
