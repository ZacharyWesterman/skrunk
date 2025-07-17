"""application.types.document"""

from typing import TypedDict
from datetime import datetime
from .usermindata import UserMinData


class Document(TypedDict):
	id: str
	title: str
	body: str
	body_html: str
	created: datetime
	updated: datetime | None
	creator: UserMinData
