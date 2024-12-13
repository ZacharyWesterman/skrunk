import application
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='Skrunk Server',
	)

	parser.add_argument('--blob-path', action='store', default=None, type=str)
	parser.add_argument('--prod', action='store_true')
	parser.add_argument('--no-auth', action='store_true')
	parser.add_argument('--ip', action='store', default='0.0.0.0', type=str)
	parser.add_argument('--port', action='store', default=5000, type=int)
	parser.add_argument('--https', action='store_true')
	parser.add_argument('--data-db', action='store', default='mongodb://localhost:27017/', type=str)

	args = parser.parse_args()

	app = application.init(no_auth=args.no_auth, blob_path=args.blob_path, data_db_url=args.data_db)
	if args.prod:
		from waitress import serve
		serve(app, host=args.ip, port=args.port, threads=32, max_request_body_size=5 * 1024 * 1024 * 1024)
	else:
		app.run(args.ip, args.port, threaded=True, debug=True)
