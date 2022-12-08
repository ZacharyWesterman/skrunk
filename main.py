import application
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog = 'Flask Server',
	)

	parser.add_argument('--vid-path', action='store', default=None, type=str)
	parser.add_argument('--prod', action='store_true')
	parser.add_argument('--no-auth', action='store_true')
	parser.add_argument('--ip', action='store', default='0.0.0.0', type=str)
	parser.add_argument('--port', action='store', default=5000, type=int)
	parser.add_argument('--http', action='store_true')
	parser.add_argument('--weather-db', action='store', default='mongodb://localhost:27017/', type=str)
	parser.add_argument('--data-db', action='store', default='mongodb://localhost:27017/', type=str)

	args = parser.parse_args()

	app = application.init(no_auth=args.no_auth, vid_path=args.vid_path, data_db_url=args.data_db, weather_db_url=args.weather_db)

	if args.http:
		app.run(args.ip, args.port, debug=not args.prod, threaded=True)
	else:
		context = ('ssl/cert.pem', 'ssl/privkey.pem')
		app.run(args.ip, args.port, debug=not args.prod, threaded=True, ssl_context=context)
