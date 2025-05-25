"""application.types.repofetchfailed"""

from typing import TypedDict


class RepoFetchFailed(TypedDict):
	"""
	An error indicating that fetching repository info from GitHub failed.
	"""

	## The error message.
	message: str
