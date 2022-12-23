//periodically check api status
_.sync('weather_exec', () => api(`{
	getLastWeatherExec{
		timestamp
		users
		error
	}
}`), 60000)


window.refresh_users = async function()
{
	_('weather_users', weather.get_users())
}

window.create_user = async function()
{
	const id = $.val('create-id')
	const phone = $.val('create-phone')
	const lat = parseFloat($.val('create-lat'))
	const lon = parseFloat($.val('create-lon'))
	const max = {
		default: $.val('create-max') === '',
		disable: !$('create-has-max').checked,
		value: parseFloat($.val('create-max-')) || 0.0,
	}
	const min = {
		default: $.val('create-min') === '',
		disable: !$('create-has-min').checked,
		value: parseFloat($.val('create-min-')) || 0.0,
	}

	const fields = [ $('create-id'), $('create-phone'), $('create-lat'), $('create-lon'), $('create-max'), $('create-min') ]

	const response = await weather.create_user(id, lat, lon, phone, max, min)

	if (response.__typename !== 'UserData')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: response.message,
			buttons: ['OK']
		}).catch(() => {})
		return
	}

	refresh_users()

	for (i of fields)
	{
		i.value = ''
	}

	can_create()
}

window.delete_user = async function(username, self)
{
	var choice = await _.modal({
		title: 'Are you sure?',
		text: 'Deleting user "' + username + '" cannot be undone!',
		buttons: [
			'Yes',
			'No',
		]
	}).catch(() => 'no')

	if (choice !== 'yes') return

	self.disabled = true
	await weather.delete_user(username)
	await refresh_users()
}

window.enable_user = async function(username, self)
{
	self.disabled = true
	await weather.enable_user(username)
	await refresh_users()
}

window.disable_user = async function(username, self)
{
	self.disabled = true
	await weather.disable_user(username)
	await refresh_users()
}

window.update_user = async function(username, self)
{
	self.disabled = true
	const phone = $.val('phone-'+username)
	const lat = parseFloat($.val('lat-'+username))
	const lon = parseFloat($.val('lon-'+username))
	const max = {
		default: $.val('max-'+username) === '',
		disable: !$('has-max-'+username).checked,
		value: parseFloat($.val('max-'+username)) || 0.0,
	}
	const min = {
		default: $.val('min-'+username) === '',
		disable: !$('has-min-'+username).checked,
		value: parseFloat($.val('min-'+username)) || 0.0,
	}

	await weather.update_user(username, phone, lat, lon, max, min)
	self.disabled = false
}

window.can_create = function()
{
	const fields = [ $('create-id'), $('create-phone'), $('create-lat'), $('create-lon') ]
	for (const i of fields)
	{
		if (i.value === '')
		{
			$('create-button').disabled = true
			return
		}
	}

	$('create-button').disabled = false
}

window.unload.push(() => {
	delete window.refresh_users
	delete window.create_user
	delete window.delete_user
	delete window.enable_user
	delete window.disable_user
	delete window.update_user
	delete window.can_create
})
