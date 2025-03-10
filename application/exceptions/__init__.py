"""application.exceptions"""


class ClientError(Exception):
	"""Base class for client-related errors."""
	pass


class UserDoesNotExistError(ClientError):
	"""Raised when a user does not exist."""

	def __init__(self, username):
		"""
		Initializes the exception with a message indicating that the specified user does not exist.

		Args:
			username (str): The username that does not exist.
		"""
		super().__init__(f'User "{username}" does not exist.')


class UserExistsError(ClientError):
	"""Raised when a user already exists."""

	def __init__(self, username):
		"""
		Initializes the exception with a message indicating that the user already exists.

		Args:
			username (str): The username that already exists.
		"""
		super().__init__(f'User "{username}" already exists.')


class AuthenticationError(ClientError):
	"""Raised when authentication fails."""

	def __init__(self):
		"""
		Initializes the exception with a default message indicating authentication failure.
		"""
		super().__init__('Authentication failed.')


class BadUserNameError(ClientError):
	"""Raised when a username is invalid."""

	def __init__(self):
		"""
		Initializes the exception with a default error message indicating an invalid username.
		"""
		super().__init__('Invalid username.')


class InvalidColor(ValueError):
	"""Raised when a color string is not a valid 7-character hex color."""

	def __init__(self, value):
		"""
		Initializes the exception with a custom error message indicating that the provided string is not a valid 7-character hex color.

		Args:
			value (str): The string that is not a valid 7-character hex color.
		"""
		super().__init__(f'The string "{value}" is not a 7-character hex color.')


class InvalidSize(ValueError):
	"""Raised when a size string is not a valid CSS size."""

	def __init__(self, value):
		"""
		Initializes the exception with a message indicating that the provided string is not a valid CSS size.

		Args:
			value (str): The string that is not a valid CSS size.
		"""
		super().__init__(f'The string "{value}" is not a valid CSS size.')


class InvalidPhone(ValueError):
	"""Raised when a phone number is not exactly 10 digits."""

	def __init__(self):
		"""
		Initializes the exception with a default error message indicating that
		the phone number must be exactly 10 digits.

		Raises:
			Exception: If the phone number is not 10 digits.
		"""
		super().__init__('Phone number must be 10 digits exactly.')


class BlobDoesNotExistError(ClientError):
	"""Raised when a blob does not exist."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a message indicating that no blob exists with the given ID.

		Args:
			id (str): The ID of the blob that does not exist.
		"""
		super().__init__(f'No blob exists with ID {id}')


class BugReportDoesNotExistError(ClientError):
	"""Raised when a bug report does not exist."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a specific bug report ID.

		Args:
			id (str): The ID of the bug report that does not exist.
		"""
		super().__init__(f'No bug report exists with ID {id}')


class BookTagDoesNotExistError(ClientError):
	"""Raised when a book tag does not exist."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a specific RFID tag.

		Args:
			id (str): The RFID tag that is not associated with any book.
		"""
		super().__init__(f'No book is tagged with RFID {id}')


class BookTagExistsError(ClientError):
	"""Raised when a book tag already exists."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a specific RFID tag.

		Args:
			id (str): The RFID tag that is already associated with a book.
		"""
		super().__init__(f'A book is already tagged with RFID {id}')


class BookCannotBeShared(ClientError):
	"""Raised when a book cannot be shared."""

	def __init__(self, msg: str):
		"""
		Initializes the exception with a given message.

		Args:
			msg (str): The message describing the exception.
		"""
		super().__init__(msg)


class MissingConfig(ClientError):
	"""Raised when a required config item is missing."""

	def __init__(self, config_name: str):
		"""
		Initializes the exception with a message indicating a missing required configuration item.

		Args:
			config_name (str): The name of the missing configuration item.
		"""
		super().__init__(f'Missing required config item "{config_name}". Please contact an admin.')


class WebPushException(ClientError):
	"""Raised when there is an error sending a web push notification."""

	def __init__(self, msg: str):
		"""
		Initializes the exception with a custom error message.

		Args:
			msg (str): The custom error message to be included in the exception.
		"""
		super().__init__(f'Error sending notification: {msg}')


class InvalidSubscriptionToken(ClientError):
	"""Raised when a notification subscription token is invalid."""

	def __init__(self):
		"""
		Initializes the exception with a default error message indicating an invalid notification subscription token.
		"""
		super().__init__('Invalid notification subscription token')


class ItemExistsError(ClientError):
	"""Raised when an item already exists."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a message indicating that an item already exists with the given RFID.

		Args:
			id (str): The RFID of the item that already exists.
		"""
		super().__init__(f'An item already exists with RFID {id}')


class ItemDoesNotExistError(ClientError):
	"""Raised when an item does not exist."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a message indicating that no item was found with the given ID.

		Args:
			id (str): The ID of the item that was not found.
		"""
		super().__init__(f'No item found with ID {id}')


class FeedDoesNotExistError(ClientError):
	"""Raised when a feed does not exist."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a specific feed ID.

		Args:
			id (str): The ID of the feed that was not found.
		"""
		super().__init__(f'No feed found with ID "{id}"')


class FeedDocumentDoesNotExistError(ClientError):
	"""Raised when a feed document does not exist."""

	def __init__(self, id: str):
		"""
		Initializes the exception with a specific feed document ID.

		Args:
			id (str): The ID of the feed document that was not found.
		"""
		super().__init__(f'No feed document found with ID "{id}"')


class InvalidFeedKindError(ClientError):
	"""Raised when a feed kind is not supported."""

	def __init__(self, kind: str):
		"""
		Initializes the exception with a message indicating that feeds of the specified kind are not supported.

		Args:
			kind (str): The type of feed that is not supported.
		"""
		super().__init__(f'Feeds of kind "{kind}" are not supported')
