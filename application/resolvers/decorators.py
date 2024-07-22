from application.exceptions import ClientError

#Return common (non-server) errors to the client, without crashing.
def handle_client_exceptions(func):
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except ClientError as e:
			return { '__typename': e.__class__.__name__, 'message': str(e) }

	return wrapper
