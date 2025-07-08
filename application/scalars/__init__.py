"""application.scalars"""

from . import color, date, datetime, long, phone, size

## The list of all custom scalar types defined in the application
scalars = [
	phone.scalar,
	datetime.scalar,
	color.scalar,
	size.scalar,
	date.scalar,
	long.scalar,
]
