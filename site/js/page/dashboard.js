window.EnabledModules = [] //These are loaded on page load
let ModuleConfig = {}
let HaveModelViewer = false

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

	$.hide('content')
	await api.snippit('dashboard_header').then(res => $('content').innerHTML = res)

	set_title()

	let chart_data = await api(`{countAllUserBooks { owner { username display_name } count }}`)
	chart_data = chart_data.sort((a,b) => b.count - a.count )

	await chart.bar('user-book-chart', chart_data.map(i => i.owner.display_name), chart_data.map(i => i.count), true)

	setTimeout(() => $.show('content'), 200)
}

window.new_xkcd = async () =>
{
	const res = await api.get_json('xkcd')
	$('xkcd').innerHTML = `
	<h3 style="text-align:center;">${res.title}</h3>
	<div title="${res.alt}" style="text-align: center;">
		<img style="max-width: 100%;" src="${res.img}" alt="${safe_html(res.alt)}"/>
	</div>
	`
}

window.set_navbar = function(name)
{
	let result = []
	for (let config of ModuleConfig[name])
	{
		if (config.module && !EnabledModules.includes(config.module)) continue
		if (config.perms && SelfUserData.perms.filter(x => config.perms.includes(x)).length !== config.perms.length) continue

		let btn_config = [config.icon, config.goto ? `set_navbar('${config.goto}'); ${config.action}` : config.action, config.text]
		if (config.class) btn_config.push(config.class)

		result.push(btn_config)
	}

	_('navbar', result)
}

window.reset_modules = modules => {
	EnabledModules = modules
	set_navbar('default')
}

async function init()
{
	//Periodically check for any unread notifications
	async function check_notifs()
	{
		push.show_notifs()
		setTimeout(check_notifs, 30000) //Check once every 30 seconds
	}
	check_notifs()

	const promise = api('{getEnabledModules}')
	const promise2 = api.get_json('config/navbar.json')

	await query.require('users')

	//Load user theme (regardless of cookies)
	query.users.get(api.username).then(async data => {
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

		ModuleConfig = await promise2
		promise.then(reset_modules)
	})

	const page = (new URLSearchParams(location.search)).get('page')
	await (page ? dashnav(page) : load_dashboard())

	await promise
	await promise2

	api.preload()
}

init()
