"""application.types.issuelabel"""

from typing import TypedDict
from bson.objectid import ObjectId


class IssueLabel(TypedDict):
	"""
	A GitHub issue label.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The name of the label.
	name: str
	## The color of the label in hex format.
	color: str
	## A description of the label.
	description: str
