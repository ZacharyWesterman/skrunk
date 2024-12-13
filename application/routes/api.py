import ariadne
import json
from flask import jsonify, request, Response
from . import auth

application = None


def graphql() -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	data = request.get_json()
	success, result = ariadne.graphql_sync(application.schema, data, context_value=request, debug=application.config.get('DEBUG'))

	if not success:
		result_code = 400
	elif result.get('errors'):
		result_code = 500
	else:
		result_code = 200

	return jsonify(result), result_code
