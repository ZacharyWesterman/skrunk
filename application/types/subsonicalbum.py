"""application.types.subsonicalbum"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class SubsonicAlbum(TypedDict):
	"""
	A type representing an album in Subsonic.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The unique identifier for the album.
	id: str
	## The parent directory ID of the album.
	parent: str
	## Indicates whether the album is a directory.
	isDir: bool
	## The title of the album.
	title: str
	## The album name.
	album: str
	## The artist of the album.
	artist: str
	## The year the album was released, if available.
	year: int | None
	## The genre of the album, if available.
	genre: str | None
	## The cover art URL for the album, if any.
	coverArt: str | None
	## The number of times the album has been played.
	playCount: int
	## The creation date and time of the album.
	created: datetime
