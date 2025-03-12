"""application.scalars"""

from . import datetime, date, phone, color, size, long

## The list of all custom scalar types defined in the application
scalars = [
	phone.scalar,
	datetime.scalar,
	color.scalar,
	size.scalar,
	date.scalar,
	long.scalar,
]
