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

class BadUserNameError(ClientError):
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

class BugReportDoesNotExistError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'No bug report exists with ID {id}')

class BookTagDoesNotExistError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'No book is tagged with RFID {id}')

class BookTagExistsError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'A book is already tagged with RFID {id}')

class BookCannotBeShared(ClientError):
	def __init__(self, msg: str):
		super().__init__(msg)

class MissingConfig(ClientError):
	def __init__(self, config_name: str):
		super().__init__(f'Missing required config item "{config_name}". Please contact an admin.')

class WebPushException(ClientError):
	def __init__(self, msg: str):
		super().__init__(f'Error sending notification: {msg}')

class InvalidSubscriptionToken(ClientError):
	def __init__(self):
		super().__init__('Invalid notification subscription token')

class ItemExistsError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'An item already exists with RFID {id}')

class FeedDoesNotExistError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'No feed found with ID "{id}"')

class FeedDocumentDoesNotExistError(ClientError):
	def __init__(self, id: str):
		super().__init__(f'No feed document found with ID "{id}"')

class InvalidFeedKindError(ClientError):
	def __init__(self, kind: str):
		super().__init__(f'Feeds of kind "{kind}" are not supported')
