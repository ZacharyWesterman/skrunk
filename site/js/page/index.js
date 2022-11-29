document.title = 'Authenticate'

window.login = function(can_error = true)
{
	api.authenticate($.val('username'), $.val('password')).then(success => {
		if (success)
		{
			api.write_cookies()
			delete window.login
			window.location.href = '/'
		}
		else if (can_error)
		{
			$('errormsg').innerText = 'Invalid Credentials'
		}
	})
}
