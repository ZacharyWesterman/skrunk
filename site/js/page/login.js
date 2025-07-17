document.title = 'Authenticate'

export function login() {
	api.authenticate($.val('username').toLowerCase(), $.val('password')).then(() => {
		api.write_cookies()
		delete window.login
		window.location.href = window.location.href
	}).catch((err) => {
		$('errormsg').innerText = err.message || 'An unknown error occurred during login.'
	})
}
