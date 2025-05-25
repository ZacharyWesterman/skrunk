from typing import TypedDict
from datetime import datetime
from .bugcomment import BugComment


class BugReport(TypedDict):
	id: str
	created: datetime
	creator: str
	body: str
	body_html: str
	convo: list[BugComment]
	resolved: bool
