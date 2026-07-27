"""Skrunk Server Main Entry Point"""

from pathlib import Path

import application

if __name__ == '__main__':
	args, app = application.new('Skrunk Server')

	if args.prod:
		from waitress import serve
		serve(app, host=args.ip, port=args.port, threads=32, max_request_body_size=5 * 1024 * 1024 * 1024)
	else:
		# Debug build will restart when files change.
		# Make sure schema files are included here.
		extra_files = [
			str(i) for i in Path('application/schema').iterdir()
		]

		app.run(args.ip, args.port, threaded=True, debug=True, extra_files=extra_files)
