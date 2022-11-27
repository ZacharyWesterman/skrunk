import application
from sys import argv

app = application.init()

if __name__ == '__main__':
	ip = '0.0.0.0'
	port = 5000
	debug = '--prod' not in argv

	if '--http' in argv:
		app.run(ip, port, debug=debug)
	else:
		context = ('ssl/cert.pem', 'ssl/privkey.pem')
		app.run(ip, port, debug=debug, ssl_context=context)
