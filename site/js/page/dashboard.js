import Yace from 'https://unpkg.com/yace?module' //For code editing textareas
window.Yace = Yace

//Load user theme (regardless of cookies)
query.users.get(api.username).then(data => {
	if (data.__typename !== 'UserData')
	{
		//If user data does not exist, we don't want them to have access. Kick them out.
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: data.message,
			buttons: ['OK']
		}).then(() => api.logout()).catch(() => {})
	}

	//Load user colors
	for (var i of data.theme.colors || [])
	{
		_.css.set_var(i.name, i.value)
	}

	//Load user sizes
	for (var i of data.theme.sizes || [])
	{
		_.css.set_var(i.name, i.value)
	}

	//Load navbar based on user perms
	_('navbar', data.perms)
})
