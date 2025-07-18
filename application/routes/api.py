"""application.routes.api"""

from typing import Any

import ariadne
from flask import Response, jsonify, request

from . import auth

application: Any = None


def graphql() -> Response:
	"""
	Handle API requests for GraphQL queries.

	Returns:
		Response: A Flask Response object containing the result of the GraphQL query.
	"""

	if not auth.authorized():
		return Response('Access denied.', 403)

	data = request.get_json()
	success, result = ariadne.graphql_sync(
		application.schema,
		data,
		context_value=request,
		debug=application.config.get('DEBUG')
	)

	if not success:
		result_code = 400
	elif result.get('errors'):
		result_code = 500
	else:
		result_code = 200

	response = jsonify(result)
	response.status_code = result_code

	return response
