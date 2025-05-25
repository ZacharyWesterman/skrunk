"""application.types.repositoryissue"""

from typing import TypedDict
from .issuelabel import IssueLabel


class RepositoryIssue(TypedDict):
	"""
	A type representing a GitHub issue.
	"""

	## The title of the issue.
	title: str
	## The state of the issue, e.g. 'open', 'closed'.
	state: str
	## The number of the issue in the repository.
	number: int
	## A list of labels on the issue.
	labels: list[IssueLabel]
