"""application.types.bugcomment"""

from typing import TypedDict
from datetime import datetime


class BugComment(TypedDict):
	created: datetime
	creator: str
	body: str
	body_html: str
