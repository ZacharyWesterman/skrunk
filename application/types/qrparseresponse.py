from typing import TypedDict


class QRParseResponse(TypedDict):
	"""
	A type for the result of parsing a QR code.
	"""

	## The parsed data from the QR code, if no error occurred
	data: str | None
	## The error message, if an error occurred
	error: str | None
