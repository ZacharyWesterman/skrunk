"""application.types.documentlist"""

from typing import TypedDict
from bson.objectid import ObjectId
from .document import Document


class DocumentList(TypedDict):
	## The unique identifier of the document.
	_id: ObjectId
	documents: list[Document]
