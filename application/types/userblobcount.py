"""application.types.userblobcount"""

from typing import TypedDict
from bson.objectid import ObjectId
from .usermindata import UserMinData


class UserBlobCount(TypedDict):
	"""
	Blob count information for a user.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## Minimal user data for the uploader of the blob.
	creator: UserMinData
	## The total number of blobs uploaded by the user.
	count: int
