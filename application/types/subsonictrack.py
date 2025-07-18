"""application.types.subsonictrack"""

from typing import TypedDict
from bson.objectid import ObjectId


class SubsonicTrack(TypedDict):
	"""
	A type representing a track in Subsonic.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The unique identifier for the track.
	id: str
	## The name of the track.
	title: str
	## The duration of the track in seconds.
	duration: int
