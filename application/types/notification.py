"""application.types.notification"""

from typing import TypedDict
from datetime import datetime


class Notification(TypedDict):
	"""
	Information about a notification sent to a user.
	"""

	## The username of the notification recipient.
	recipient: str
	## The date and time when the notification was created.
	created: datetime
	## The notification message.
	message: str
	## The category of the notification, such as 'general', 'alert', etc.
	category: str
	## The number of devices the notification was sent to.
	device_count: int
	## Whether the notification has been read by the user.
	read: bool
	## The unique identifier for the notification.
	id: str
