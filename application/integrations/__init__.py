"""application.integrations"""

from application.exceptions import SubsonicError

from . import subsonic

SUBSONIC: subsonic.SubsonicClient | None = None


def init_subsonic(url: str | None, username: str | None, password: str | None) -> subsonic.SubsonicClient:
	"""
	Initializes the global Subsonic client with the provided credentials.

	Args:
		url (str | None): The URL of the Subsonic server.
		username (str | None): The username for authentication.
		password (str | None): The password for authentication.

	Raises:
		SubsonicError: If any of the required parameters (url, username, password) are missing or empty.
	"""
	if not url or not username or not password:
		raise SubsonicError()

	global SUBSONIC
	SUBSONIC = subsonic.SubsonicClient(url, username, password)
	return SUBSONIC


def get_subsonic() -> subsonic.SubsonicClient | None:
	"""
	Returns the current instance of the Subsonic client if available.

	Returns:
		subsonic.SubsonicClient | None: The Subsonic client instance if initialized, otherwise None.
	"""
	return SUBSONIC
