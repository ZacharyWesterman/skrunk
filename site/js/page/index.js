document.title = 'Authenticate'

function login(can_error = true)
{
	api.authenticate($.val('username'), $.val('password')).then(success => {
		if (success)
		{
			api.write_cookies()
			window.location.href = '/'
		}
		else if (can_error)
		{
			$('errormsg').innerText = 'Invalid Credentials'
		}
	})
}
