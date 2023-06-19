import Yace from 'https://unpkg.com/yace?module' //For code editing textareas
window.Yace = Yace

window.fullscreen = function()
{
	if (!document.fullscreenElement)
	{
		const elem = document.documentElement
		if (elem.requestFullscreen) elem.requestFullscreen()
		else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen()
	}
	else
	{
		document.exitFullscreen()
	}
}

window.set_book_dashboard_buttons = function()
{
	dashnav('/html/books.html')
	_('navbar', [
		['arrow-up', "reset_dashboard_buttons()"],
		['book', "dashnav('/html/books.html')"],
		['bookmark', "dashnav('/html/books_new.html')"],
		['bug', "dashnav('/html/bugs.html')", 'bottom'],
		['expand', 'fullscreen()', 'bottom'],
	])
}

window.set_user_dashboard_buttons = function()
{
	dashnav('/html/user.html')
	_('navbar', [
		['arrow-up', "reset_dashboard_buttons()"],
		['user-pen', "dashnav('/html/user.html')"],
		['palette', "dashnav('/html/edit_theme.html')"],
		['bug', "dashnav('/html/bugs.html')", 'bottom'],
		['expand', 'fullscreen()', 'bottom'],
	])
}

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
		return
	}

	window.SelfUserData = data

	//Wipe theme data
	_.css.wipe()

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

	window.reset_dashboard_buttons = async function()
	{
		//Load navbar based on user perms
		let buttons = [
			['right-from-bracket', "api.logout()"],
			['user-pen', "set_user_dashboard_buttons()"],
			['book', "set_book_dashboard_buttons()"],
			['server', "dashnav('/html/file_list.html')"],
			['file-arrow-up', "_.modal.upload()"],
			['bug', "dashnav('/html/bugs.html')", 'bottom'],
			['expand', 'fullscreen()', 'bottom'],
		]

		if (data.perms.includes('admin'))
		{
			buttons.push(['users', "dashnav('/html/users.html')", 'alt'])
			buttons.push(['cloud-bolt', "dashnav('/html/weather_users.html')", 'alt'])
		}

		await _('navbar', buttons)
	}

	reset_dashboard_buttons().then(() => {
		$('content').innerText = ''
	})
})
