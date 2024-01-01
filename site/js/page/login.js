document.title = 'Authenticate'

export function login()
{
	api.authenticate($.val('username').toLowerCase(), $.val('password')).then(success => {
		if (success)
		{
			api.write_cookies()
			delete window.login
			window.location.href = window.location.href
		}
		else
		{
			$('errormsg').innerText = 'Invalid Credentials'
		}
	})
}
