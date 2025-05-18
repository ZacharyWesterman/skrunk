from typing import TypedDict
from .subsonicalbum import SubsonicAlbum


class SubsonicSearch(TypedDict):
	album: list[SubsonicAlbum | None]
