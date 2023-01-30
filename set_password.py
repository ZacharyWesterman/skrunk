#!/usr/bin/env python3
#Set user password via command-line

import application
import argparse
from application.db.users import update_user_password
import bcrypt, hashlib

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog = 'Script Interface',
	)

	parser.add_argument('--blob-path', action='store', default=None, type=str)
	parser.add_argument('--no-auth', action='store_true')
	parser.add_argument('--weather-db', action='store', default='mongodb://localhost:27017/', type=str)
	parser.add_argument('--data-db', action='store', default='mongodb://localhost:27017/', type=str)
	parser.add_argument('--username', action='store', type=str, required=True)
	parser.add_argument('--passhash', action='store', type=str, required=True)

	args = parser.parse_args()

	app = application.init(no_auth=args.no_auth, blob_path=args.blob_path, data_db_url=args.data_db, weather_db_url=args.weather_db)

	update_user_password(args.username, args.passhash)
