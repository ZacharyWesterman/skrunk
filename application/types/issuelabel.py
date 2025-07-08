"""application.types.issuelabel"""

from typing import TypedDict


class IssueLabel(TypedDict):
	"""
	A GitHub issue label.
	"""

	## The name of the label.
	name: str
	## The color of the label in hex format.
	color: str
	## A description of the label.
	description: str
