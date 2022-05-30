class ClientError(Exception):
	pass

class UserDoesNotExistError(ClientError):
	pass

class AuthenticationError(ClientError):
	pass
