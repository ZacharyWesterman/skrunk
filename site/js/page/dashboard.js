window.EnabledModules = [] //These are loaded on page load

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
	dashnav('books')
	let buttons = [
		['arrow-up', "reset_dashboard_buttons()", 'Back'],
		['book', "dashnav('books')", 'Library'],
		['bookmark', "dashnav('books_new')", 'Catalog Books'],
	]
	if (EnabledModules.includes('bugs')) buttons.push(['bug', "dashnav('bugs')", 'Bug Tracker', 'bottom'])
	if (!environment.ios) buttons.push(['expand', 'fullscreen()', 'Toggle Fullscreen', 'bottom'])
	_('navbar', buttons)
}

window.set_user_dashboard_buttons = function()
{
	dashnav('user')
	let buttons = [
		['arrow-up', "reset_dashboard_buttons()", 'Back'],
		['user-pen', "dashnav('user')", 'Edit User Info'],
	]
	if (EnabledModules.includes('theme')) buttons.push(['palette', "dashnav('edit_theme')", 'Customize Theme'])
	if (EnabledModules.includes('bugs')) buttons.push(['bug', "dashnav('bugs')", 'Bug Tracker', 'bottom'])
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
	]

	if (EnabledModules.includes('books')) buttons.push(['book', "set_book_dashboard_buttons()", 'Library'])
	if (EnabledModules.includes('files')) {
		buttons.push(['hard-drive', "dashnav('file_list')", 'Files'])
		buttons.push(['file-arrow-up', "_.modal.upload()", 'Upload Files'])
	}

	if (EnabledModules.includes('bugs')) buttons.push(['bug', "dashnav('bugs')", 'Bug Tracker', 'bottom'])
	if (!environment.ios) buttons.push(['expand', 'fullscreen()', 'Toggle Fullscreen', 'bottom'])

	if (SelfUserData.perms.includes('admin'))
	{
		buttons.push(['users', "dashnav('users')", 'Edit Users (Admin)', 'alt'])
		if (EnabledModules.includes('weather'))
			buttons.push(['cloud-bolt', "dashnav('weather_users')", 'Weather Users (Admin)', 'alt'])
		buttons.push(['gear', "dashnav('server_settings')", 'Server Settings', 'alt'])
	}

	await _('navbar', buttons)
}

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
	environment.set_page('/', 'home')
	await api.snippit('dashboard_header').then(res => $('content').innerHTML = res)
	set_title()

	//Load random xkcd comic
	api.get_json('xkcd').then(res => {
		$('xkcd').innerHTML = `<br><img width="100%" height="auto" src="${res.img}"/>`
	})
}

window.reset_modules = async modules => {
	EnabledModules = modules
	reset_dashboard_buttons()
}

async function init()
{
	const promise = api('{getEnabledModules}')

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

		promise.then(reset_modules)
	})

	const page = (new URLSearchParams(location.search)).get('page')
	if (page === null)
		load_dashboard()
	else
		dashnav(page)
}

init()