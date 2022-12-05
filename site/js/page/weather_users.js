var weather_users = []

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

	const fields = [ $('create-id'), $('create-phone'), $('create-lat'), $('create-lon') ]

	for (i of fields) i.disabled = true

	const response = await weather.create_user(id, lat, lon, phone)

	if (response.__typename !== 'UserData')
	{
		_.modal({
			title: '<span class="error">ERROR</span>',
			text: response.message,
			buttons: ['OK']
		}).catch(() => {})
		for (i of fields) i.disabled = false
		return
	}

	refresh_users()

	for (i of fields)
	{
		i.disabled = false
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

	await weather.update_user(username, phone, lat, lon)
	self.disabled = false
}

window.can_create = function()
{
	const fields = [ $('create-id'), $('create-phone'), $('create-lat'), $('create-lon') ]
	for (i of fields)
	{
		if (i.value === '')
		{
			$('create-button').disabled = true
			return
		}
	}

	$('create-button').disabled = false
}

refresh_users()
