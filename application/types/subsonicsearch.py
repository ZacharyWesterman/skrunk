"""application.types.subsonicsearch"""

from typing import TypedDict
from bson.objectid import ObjectId
from .subsonicalbum import SubsonicAlbum


class SubsonicSearch(TypedDict):
	"""
	The results of a Subsonic search query.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## A list of albums matching the search query.
	album: list[SubsonicAlbum]
