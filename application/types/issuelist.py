"""application.types.issuelist"""

from typing import TypedDict
from .repositoryissue import RepositoryIssue


class IssueList(TypedDict):
	"""
	A list of GitHub issues.
	"""

	## A list of issues in the repository.
	issues: list[RepositoryIssue]
