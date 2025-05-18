from typing import TypedDict
from datetime import datetime


class Blob(TypedDict):
	id: str
	created: datetime
	creator: str
	name: str
	ext: str
	mimetype: str
	size: int
	tags: list[str]
	preview: str
	thumbnail: str
	hidden: bool
	ephemeral: bool
	references: int
