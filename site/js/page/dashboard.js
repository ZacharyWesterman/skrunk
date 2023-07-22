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
	let buttons = [
		['arrow-up', "reset_dashboard_buttons()", 'Back'],
		['book', "dashnav('/html/books.html')", 'Library'],
		['bookmark', "dashnav('/html/books_new.html')", 'Catalog Books'],
		['bug', "dashnav('/html/bugs.html')", 'Bug Tracker', 'bottom'],
	]
	if (!environment.ios) buttons.push(['expand', 'fullscreen()', 'Toggle Fullscreen', 'bottom'])
	_('navbar', buttons)
}

window.set_user_dashboard_buttons = function()
{
	dashnav('/html/user.html')
	let buttons = [
		['arrow-up', "reset_dashboard_buttons()", 'Back'],
		['user-pen', "dashnav('/html/user.html')", 'Edit User Info'],
		['palette', "dashnav('/html/edit_theme.html')", 'Customize Theme'],
		['bug', "dashnav('/html/bugs.html')", 'Bug Tracker', 'bottom'],
	]
	if (!environment.ios) buttons.push(['expand', 'fullscreen()', 'Toggle Fullscreen', 'bottom'])
	_('navbar', buttons)
}

window.reset_dashboard_buttons = async () =>
{
	//Load navbar based on user perms
	let buttons = [
		['right-from-bracket', "api.logout()", 'Logout'],
		['home', 'load_dashboard()', 'Home'],
		['user-pen', "set_user_dashboard_buttons()", 'Edit User Info'],
		['book', "set_book_dashboard_buttons()", 'Library'],
		['hard-drive', "dashnav('/html/file_list.html')", 'Files'],
		['file-arrow-up', "_.modal.upload()", 'Upload Files'],
		['bug', "dashnav('/html/bugs.html')", 'Bug Tracker', 'bottom'],
	]

	if (!environment.ios) buttons.push(['expand', 'fullscreen()', 'Toggle Fullscreen', 'bottom'])

	if (SelfUserData.perms.includes('admin'))
	{
		buttons.push(['users', "dashnav('/html/users.html')", 'Edit Users (Admin)', 'alt'])
		buttons.push(['cloud-bolt', "dashnav('/html/weather_users.html')", 'Weather Users (Admin)', 'alt'])
	}

	await _('navbar', buttons)
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
	for (const i of data.theme.colors || [])
	{
		_.css.set_var(i.name, i.value)
	}

	//Load user sizes
	for (const i of data.theme.sizes || [])
	{
		_.css.set_var(i.name, i.value)
	}

	reset_dashboard_buttons()
	load_dashboard()
})

let HaveModelViewer = false

window.load_model_viewer = () =>
{
	if (!HaveModelViewer)
	{
		HaveModelViewer = true
		let abort = new AbortController()
		let im = import('https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js') //Only import this when it's needed
		let slow_connection = false
		const fn = () => {
			slow_connection = true
			show_raw_error_message('Loading model viewer. This will only happen once...')
			slow_load = setTimeout(fn, 6000)
		}

		let slow_load = setTimeout(fn, 1000)

		im.then(() => {
			if (slow_connection)
			{
				clear_error_message()
				show_raw_error_message('Model viewer loaded!')
			}
			clearTimeout(slow_load)
		})
	}

	return ''
}

window.load_dashboard = async () =>
{
	await api.snippit('dashboard_header').then(res => $('content').innerHTML = res)

	//Load random xkcd comic
	api.get_json('xkcd').then(res => {
		$('xkcd').innerHTML = `<br><img width="100%" height="auto" src="${res.img}"/>`
	})
}