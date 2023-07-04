from application.db import init_db
from application.db.book import refresh_book_data, next_out_of_date_book_rfid
from datetime import datetime, timedelta

if __name__ == '__main__':
	init_db() #init, assuming local server

	from application.db.book import db

	#Sync books that were added more than 2 weeks ago
	before = datetime.utcnow() - timedelta(weeks=2)
	rfid = next_out_of_date_book_rfid(before)

	if rfid is not None:
		refresh_book_data(rfid)