from . import auth

def init(application) -> None:
	auth.application = application

	application.route('/auth')(auth.auth_user)
	application.route('/auth/verify')(auth.verify_token)