"""application.types.issuelist"""

from typing import TypedDict
from bson.objectid import ObjectId
from .repositoryissue import RepositoryIssue


class IssueList(TypedDict):
	"""
	A list of GitHub issues.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## A list of issues in the repository.
	issues: list[RepositoryIssue]
