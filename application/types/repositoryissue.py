"""application.types.repositoryissue"""

from typing import TypedDict
from .issuelabel import IssueLabel


class RepositoryIssue(TypedDict):
	title: str
	state: str
	number: int
	labels: list[IssueLabel]
