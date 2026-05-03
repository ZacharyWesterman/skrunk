"""Skrunk Server Main Entry Point"""

import argparse

import application

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='Skrunk Server',
	)

	parser.add_argument(
		'--blob-path', action='store', default=None, type=str, help='The blob data storage location'
	)
	parser.add_argument('--prod', action='store_true', help='Run in production mode')
	parser.add_argument('--no-auth', action='store_true', help='Disable authentication')
	parser.add_argument(
		'--ip', action='store', default='0.0.0.0', type=str, help='The IP address to bind to'
	)
	parser.add_argument('--port', action='store', default=5000, type=int, help='The port to bind to')
	parser.add_argument('--https', action='store_true', help='Enable HTTPS')
	parser.add_argument(
		'--database', action='store', default='mongodb://localhost:27017/', type=str,
		help='The connection URI of the mongodb database'
	)
	parser.add_argument('--bundle', action='store_true', help='Bundle common files to improve performance.')

	args = parser.parse_args()

	if args.bundle:
		application.bundler.bundle()
	else:
		application.bundler.no_bundle()

	app = application.init(no_auth=args.no_auth, blob_path=args.blob_path, database_url=args.database)
	if args.prod:
		from waitress import serve
		serve(app, host=args.ip, port=args.port, threads=32, max_request_body_size=5 * 1024 * 1024 * 1024)
	else:
		app.run(args.ip, args.port, threaded=True, debug=True)
