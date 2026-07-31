"""Skrunk Server Main Entry Point"""

import time
from datetime import datetime
from pathlib import Path

import application

if __name__ == '__main__':
	args, app = application.new('Skrunk Server')

	if args.wait_for_port:
		if application.port_in_use(args.port):
			print(f'Port {args.port} is already in use. Waiting for it to be available...', flush=True)

			# Wait for port to be available
			begin = datetime.now()
			while application.port_in_use(args.port):
				time.sleep(0.1)
			end = datetime.now()
			print(f'Grabbed port {args.port} after {end - begin}.', flush=True)

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
