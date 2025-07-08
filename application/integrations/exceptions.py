"""
Exceptions that may be raised by various integrations.
"""


class ApiFailedError(Exception):
	"""
	Exception raised when an API call fails.

	This exception is intended to be used when an API request does not succeed,
	either due to network issues, invalid responses, or other related errors.

	Attributes:
		message (str): Explanation of the error.
	"""


class UnsupportedFileFormat(Exception):
	"""
	Exception raised for unsupported file formats.

	Attributes:
		filename (str): The name of the file with the unsupported format.
	"""

	def __init__(self, filename: str) -> None:
		"""
		Initializes the exception with a message indicating an unsupported file format.

		Args:
			filename (str): The name of the file with the unsupported format.
		"""
		super().__init__(f'Unsupported file format for {filename}')


class RepoFetchFailed(Exception):
	"""
	Exception raised when a repository fetch operation fails.

	Attributes:
		url (str): The URL of the repository that failed to fetch.
		text (str): The error message associated with the fetch failure.
	"""

	def __init__(self, url: str, text: str) -> None:
		"""
		Initializes the exception with a custom error message.

		Args:
			url (str): The URL that was requested.
			text (str): The error message text.

		Returns:
			None
		"""
		super().__init__(f'Unable to fetch data due to error: {text}. Request URL: {url}')
