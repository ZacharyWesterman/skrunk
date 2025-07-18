"""application.types.qrparseresponse"""

from typing import TypedDict
from bson.objectid import ObjectId


class QRParseResponse(TypedDict):
	"""
	A type for the result of parsing a QR code.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The parsed data from the QR code, if no error occurred
	data: str | None
	## The error message, if an error occurred
	error: str | None
