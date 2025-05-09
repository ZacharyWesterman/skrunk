await mutate.require('weather')
await query.require('weather')

export function init() {
	if (EnabledModules.includes('weather')) {
		//periodically check api status
		_.sync('weather_exec', query.weather.last_execution, 60000)
	}
}

export async function refresh_users() {
	let res = await query.weather.users()
	if (environment.page === 'user') {
		//If single user view, only show info for that user.
		res = res.filter(user => user.username === api.username)
	}
	await _('weather_users', res)
}

export async function create_user() {
	const id = $.val('create-id')
	const lat = parseFloat($.val('create-lat'))
	const lon = parseFloat($.val('create-lon'))
	const max = {
		default: $.val('create-max') === '',
		disable: !$('create-has-max').checked,
		value: parseFloat($.val('create-max')) || 0.0,
	}
	const min = {
		default: $.val('create-min') === '',
		disable: !$('create-has-min').checked,
		value: parseFloat($.val('create-min')) || 0.0,
	}

	const fields = [$('create-id'), $('create-lat'), $('create-lon'), $('create-max'), $('create-min')]

	const response = await mutate.weather.create_user(id, lat, lon, max, min)

	if (response.__typename !== 'WeatherUser') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: response.message,
			buttons: ['OK']
		}).catch(() => { })
		return
	}

	_.modal.checkmark()
	refresh_users()

	for (let i of fields) {
		i.value = ''
	}

	can_create()
}

export async function delete_user(username, self) {
	const choice = await _.modal({
		title: 'Are you sure?',
		text: 'Deleting user "' + username + '" cannot be undone!',
		buttons: [
			'Yes',
			'No',
		]
	}).catch(() => 'no')

	if (choice !== 'yes') return

	self.disabled = true
	await mutate.weather.delete_user(username)
	_.modal.checkmark()
	await refresh_users()
}

export async function enable_user(username, self) {
	self.disabled = true
	await mutate.weather.enable_user(username)
	_.modal.checkmark()
	await refresh_users()
}

export async function disable_user(username, self) {
	self.disabled = true
	await mutate.weather.disable_user(username)
	_.modal.checkmark()
	await refresh_users()
}

export async function update_user(username, self) {
	const lat = parseFloat($.val('lat-' + username))
	const lon = parseFloat($.val('lon-' + username))
	const max = {
		default: $.val('max-' + username) === '',
		disable: !$('has-max-' + username).checked,
		value: parseFloat($.val('max-' + username)) || 0.0,
	}
	const min = {
		default: $.val('min-' + username) === '',
		disable: !$('has-min-' + username).checked,
		value: parseFloat($.val('min-' + username)) || 0.0,
	}

	const res = await mutate.weather.update_user(username, lat, lon, max, min)

	if (res.__typename !== 'WeatherUser') {
		_.modal.error(res.message)
		return
	}

	const id = `icon-${self.id.replace('has-', '')}`
	$.blink(id)
}

export function can_create() {
	const fields = [$('create-id'), $('create-lat'), $('create-lon')]
	for (const i of fields) {
		if (i.value === '') {
			$('create-button').disabled = true
			return
		}
	}

	$('create-button').disabled = false
}

export function maps_info() {
	_.modal({
		title: 'Getting Your Coordinates',
		text: api.snippit('latitude-longitude'),
		buttons: ['OK'],
	})
}
