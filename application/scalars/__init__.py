"""application.scalars"""

from . import datetime, date, phone, color, size, long

scalars = [
	phone.scalar,
	datetime.scalar,
	color.scalar,
	size.scalar,
	date.scalar,
	long.scalar,
]
