import application

app = application.init()

if __name__ == '__main__':
	context = ('ssl/cert.pem', 'ssl/privkey.pem')
	app.run('0.0.0.0', 5000, debug=True, ssl_context=context)
