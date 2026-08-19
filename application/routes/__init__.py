"""application.routes"""

from datetime import UTC, datetime

from flask import Response, jsonify

from . import api, auth, blob, misc, site, wopi

__last_query_at: datetime | None = None
__running_query_ct: int = 0


def tq(func):
	"""
	A decorator to track the last time a route was called, and how many responses are in-progress.

	This decorator exists purely to know when it's safe to shut down/restart the server.
	It doesn't track ANYTHING other than the quiescence of the back end.
	"""
	def wrapper(*args, **kwargs):
		global __last_query_at, __running_query_ct
		__last_query_at = datetime.now(UTC)
		__running_query_ct += 1
		result = func(*args, **kwargs)
		__running_query_ct -= 1
		return result

	wrapper.__name__ = func.__name__

	return wrapper


def init(application) -> None:
	"""
	Initialize the application routes.

	Args:
		application: The Flask application instance to which the routes will be added.
	"""

	auth.application = application
	api.application = application
	site.application = application
	blob.application = application

	application.route('/auth', methods=['POST'])(tq(auth.auth_user))
	application.route('/auth/verify', methods=['POST'])(tq(auth.verify_token))
	application.route('/auth/request-reset-code', methods=['POST'])(tq(auth.request_reset_code))
	application.route('/auth/reset', methods=['POST'])(tq(auth.reset_password))

	application.route('/api', methods=['POST'])(tq(api.graphql))
	application.route('/xkcd', methods=['GET'])(tq(misc.random_xkcd))

	application.route('/', methods=['GET'])(tq(site.main_page))
	application.route('/<path:path>', methods=['GET'])(tq(site.get))
	application.route('/favicon.ico', methods=['GET'])(tq(site.get_favicon))
	application.route('/<path:path>.png', methods=['GET'])(tq(site.get_icon))
	application.route('/<path:path>.svg', methods=['GET'])(tq(site.get_svg))

	application.route('/blob/<path:path>', methods=['GET'])(tq(blob.stream))
	application.route('/download/<path:path>', methods=['GET'])(tq(blob.download))
	application.route('/preview/<path:path>', methods=['GET'])(tq(blob.preview))
	application.route('/thumb/<path:path>', methods=['GET'])(tq(blob.thumbnail))
	application.route('/upload', methods=['POST'])(tq(blob.upload))

	application.route('/<path:jwt>/wopi/files/<path:id>/contents', methods=['GET'])(wopi.get_document_contents)
	application.route('/<path:jwt>/wopi/files/<path:id>/contents', methods=['POST'])(wopi.get_document_contents)
	application.route('/<path:jwt>/wopi/files/<path:id>', methods=['GET'])(wopi.get_document_info)

	@application.after_request
	def after_request(response):
		response.headers.add('Accept-Ranges', 'bytes')
		return response

	# Quiescence reporting doesn't need an API key.
	# Thinking is that there's nothing super valuable to
	# be gained from knowing how active the server is currently.
	@application.route('/quiescence', methods=['GET'])
	def get_quiescence() -> Response:
		return jsonify({
			'last_query': __last_query_at,
			'in_progress': __running_query_ct,
		})
