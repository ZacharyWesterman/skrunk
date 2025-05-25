"""application.types.bugreport"""

from typing import TypedDict
from datetime import datetime
from .bugcomment import BugComment


class BugReport(TypedDict):
	"""
	Information about a bug report.
	"""

	## The unique identifier for the bug report.
	id: str
	## The creation date and time of the bug report.
	created: datetime
	## The username of the creator of the bug report.
	creator: str
	## The raw text of the bug report.
	body: str
	## The HTML-rendered version of the bug report body.
	body_html: str
	## A list of comments on the bug report.
	convo: list[BugComment]
	## The status of the bug report, indicating whether it is resolved or not.
	resolved: bool
