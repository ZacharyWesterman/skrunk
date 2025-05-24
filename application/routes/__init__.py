"""application.routes"""

from . import api, auth, blob, misc, site


def init(application) -> None:
	auth.application = application
	api.application = application
	misc.application = application
	site.application = application
	blob.application = application

	application.route('/auth', methods=['POST'])(auth.auth_user)
	application.route('/auth/verify', methods=['POST'])(auth.verify_token)
	application.route('/api', methods=['POST'])(api.graphql)
	application.route('/xkcd', methods=['GET'])(misc.random_xkcd)

	application.route('/', methods=['GET'])(site.main_page)
	application.route('/<path:path>', methods=['GET'])(site.get)
	application.route('/<path:path>.png', methods=['GET'])(site.get_icon)
	application.route('/<path:path>.svg', methods=['GET'])(site.get_svg)

	application.route('/blob/<path:path>', methods=['GET'])(blob.stream)
	application.route('/download/<path:path>', methods=['GET'])(blob.download)
	application.route('/preview/<path:path>', methods=['GET'])(blob.preview)
	application.route('/upload', methods=['POST'])(blob.upload)

	@application.after_request
	def after_request(response):
		response.headers.add('Accept-Ranges', 'bytes')
		return response
