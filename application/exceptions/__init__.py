class ClientError(Exception):
	pass

class UserDoesNotExistError(ClientError):
	def __init__(self, username):
		super().__init__(f'User "{username}" does not exist.')

class UserExistsError(ClientError):
	def __init__(self, username):
		super().__init__(f'User "{username}" already exists.')

class AuthenticationError(ClientError):
	def __init__(self):
		super().__init__('Authentication failed.')

class InvalidUsername(ClientError):
	def __init__(self):
		super().__init__('Invalid username.')

class InvalidColor(ValueError):
	def __init__(self, value):
		super().__init__(f'The string "{value}" is not a 7-character hex color.')

class InvalidSize(ValueError):
	def __init__(self, value):
		super().__init__(f'The string "{value}" is not a valid CSS size.')

class InvalidPhone(ValueError):
	def __init__(self):
		super().__init__('Phone number must be 10 digits exactly.')

class BlobDoesNotExistError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'No blob exists with ID {id}')
