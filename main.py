import application
from sys import argv


if __name__ == '__main__':
	ip = '0.0.0.0'
	port = 5000
	debug = '--prod' not in argv
	no_auth = '--no-auth' in argv
	vid_path = '/home/zachary/Videos'

	app = application.init(no_auth=no_auth, vid_path=vid_path)

	if '--http' in argv:
		app.run(ip, port, debug=debug, threaded=True)
	else:
		context = ('ssl/cert.pem', 'ssl/privkey.pem')
		app.run(ip, port, debug=debug, threaded=True, ssl_context=context)
