"""application.types.issuelist"""

from typing import TypedDict
from .repositoryissue import RepositoryIssue


class IssueList(TypedDict):
	issues: list[RepositoryIssue]
