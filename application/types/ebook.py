"""application.types.ebook"""

from typing import TypedDict
from bson.objectid import ObjectId


class EBook(TypedDict):
	"""
	eBook information for a book.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The URL to the eBook file.
	url: str
	## The file type of the eBook, such as 'pdf', 'epub', etc.
	fileType: str
