document.title = 'Authenticate'

window.login = function()
{
	api.authenticate($.val('username'), $.val('password')).then(success => {
		if (success)
		{
			api.write_cookies()
			delete window.login
			window.location.href = '/'
		}
		else
		{
			$('errormsg').innerText = 'Invalid Credentials'
		}
	})
}

$.on.blur($('username'), $.next)
$.on.blur($('password'), login)
