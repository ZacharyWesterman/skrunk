"""application.types.subsonicsearch"""

from typing import TypedDict
from .subsonicalbum import SubsonicAlbum


class SubsonicSearch(TypedDict):
	"""
	The results of a Subsonic search query.
	"""

	## A list of albums matching the search query.
	album: list[SubsonicAlbum]
