"""application.types.booktag"""

from typing import TypedDict
from bson.objectid import ObjectId


class BookTag(TypedDict):
	"""
	A type for a tag associated with a book, typically an RFID tag or QR code.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The RFID tag or QR code associated with the book.
	rfid: str
	## The ID of the book this tag is linked to.
	bookId: str
	## The ID of the user who created the tag.
	creator: str
