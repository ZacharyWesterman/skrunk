class ClientError(Exception):
	pass

class UserDoesNotExistError(ClientError):
	pass

class UserExistsError(ClientError):
	pass

class AuthenticationError(ClientError):
	pass

class InvalidUsername(ClientError):
	pass

class LoginExpired(ClientError):
	pass
