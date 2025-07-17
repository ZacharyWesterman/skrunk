"""application.types.documentmin"""

from typing import TypedDict
from .usermindata import UserMinData
from datetime import datetime


class DocumentMin(TypedDict):
	id: str
	title: str
	creator: UserMinData
	created: datetime
