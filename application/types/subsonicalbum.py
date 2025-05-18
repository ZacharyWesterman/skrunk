from typing import TypedDict
from datetime import datetime

class SubsonicAlbum(TypedDict):
	id: str
	parent: str
	isDir: bool
	title: str
	album: str
	artist: str
	year: int
	genre: str
	coverArt: str
	playCount: int
	created: datetime

