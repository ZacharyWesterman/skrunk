await mutate.require('users')
await query.require('users')

let Perms
let UserData = {}

export async function revoke_sessions(username) {
	const self_msg = 'Are you sure you want to revoke your sessions? This will log you out of all devices, including this one.'
	const other_msg = 'Are you sure you want to revoke all sessions for user "' + username + '"? This will log them out of all devices.'

	const choice = await _.modal({
		type: 'question',
		title: 'Revoke User Sessions?',
		text: (username === api.username) ? self_msg : other_msg,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	await mutate.users.revoke(username)
	$('session-ct-' + username).innerText = await query.users.sessions(username)
	_.modal.checkmark()
}

export async function set_perms() {
	console.log(UserData)

	let new_perms = []
	let perms_changed = []
	for (const perm of Perms) {
		const checked = $('perm-' + perm.name).checked
		if (checked !== UserData.perms.includes(perm.name)) perms_changed.push(perm.name)
		if (checked) new_perms.push(perm.name)
	}
	UserData.perms = new_perms

	const res = await mutate.users.permissions(UserData.username, UserData.perms)
	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(() => { })
		return
	}

	for (const perm of perms_changed) {
		const id = `icon-perm-${perm}`
		$.blink(id)
	}

	sync_perm_descs()
}

export async function load_user_data(username, self_view = false) {
	let perms = Perms
	if (!perms) {
		perms = api.get_json('/config/permissions.json')
		perms.then(p => Perms = p)
	}

	let p2 = api('{ getUserGroups }')

	UserData = query.users.get(username)

	await _('userdata', {
		perms: perms,
		user: UserData,
		sessions: query.users.sessions(username),
		self_view: self_view,
		all_modules: api('{ getModules }'),
	})

	if (has_perm('admin')) {
		await _('usrgrp', {
			id: 'user-group',
			items: p2,
		})
		UserData.then(user_data => {
			$('user-group').value = user_data.groups ? (user_data.groups || '') : ''
		})
	}

	if (self_view) {
		push.ready.then(() => {
			$('enable-push').checked = push.subscribed
		})
	}

	perms.then ? perms.then(sync_perm_descs) : sync_perm_descs()

	api.get_json('/config/modules.json').then(modules => {
		for (let mod of modules) {
			const field = $(`module-name-${mod.id}`)
			if (field) {
				field.innerText = mod.name
				$(`module-tooltip-${mod.id}`).innerText = mod.description
			}
		}
	})

	UserData = await UserData
}

export async function update_user_module(field) {
	const module_name = field.id.substring(7)
	const disabled = !field.checked

	field.disabled = true
	const res = await mutate.users.module(api.username, module_name, disabled)

	if (res.__typename !== 'UserData') {
		_.modal.error(res.message)
		field.checked = !field.checked
	}
	else {
		field.checked = !res.disabled_modules.includes(module_name)
	}

	field.disabled = false
	$.blink(`icon-module-${module_name}`)

	const p1 = api('{ getEnabledModules }')
	const p2 = api('{ getModules }')

	p2.then(async all_modules => {
		const enabled_modules = await p1

		for (let module of all_modules) {
			const enabled = enabled_modules.includes(module)
			if ($(`module-${module}`).checked !== enabled) {
				$.blink(`icon-module-${module}`)
			}
			$(`module-${module}`).checked = enabled
		}

		reset_modules(enabled_modules)
	})
}

export async function update_groups(username) {
	const groups = $.val('user-group').split(',').map(i => i.trim()).filter(i => i.length > 0)

	const res = await api(`mutation ($username: String!, $groups: [String!]!) {
		updateUserGroups (username: $username, groups: $groups) {
			__typename
			...on UserDoesNotExistError { message }
			...on InsufficientPerms { message }
		}
	}`, {
		username: username,
		groups: groups,
	})

	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	_.modal.checkmark()
	_('usrgrp', {
		id: 'user-group',
		items: api('{ getUserGroups }'),
	}).then(() => {
		$('user-group').value = groups.join(', ')
	})
}

function sync_perm_descs() {
	for (const perm of Perms) {
		const desc = $('perm-' + perm.name).checked ? "true" : "false"
		$('perm-tooltip-' + perm.name).innerText = perm[desc]
	}
}

export async function update_password(password, username) {
	if ((password.length < 8) || (password === username) || (password.includes(username) && (password.length < username.length * 2))) {
		const criteria = [
			'Must be at least 8 characters long',
			'May not contain the username, unless it\'s at least 2&times; the length',
		]

		_.modal({
			type: 'error',
			title: 'Invalid Password',
			text: 'Password must fit <i>all</i> of the following criteria:<ul><li>' + criteria.join('</li><li>') + '</li></ul>',
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	if (password !== $.val('user-new-password2')) {
		_.modal({
			type: 'error',
			title: 'Passwords don\'t match',
			text: 'Make sure you typed the password in correctly!',
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	const hashed_pass = await api.hash(password)
	const res = await mutate.users.password(username, hashed_pass)

	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	_.modal({
		title: 'Success',
		text: 'Password has been updated.',
		buttons: ['OK'],
	})
}

export async function update_user_display_name(username) {
	const display_name = $.val('user-display-name')
	const res = await mutate.users.display_name(username, display_name)

	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	$('user-display-name').value = res.display_name
	const id = `icon-user-display-name`
	$.show(id)
	setTimeout(() => {
		$.hide(id, true)
	}, 500)
}

export async function update_user_email(username) {
	const email = $.val('user-email')

	if (email !== '') {
		const valid = $.validate.email(email)
		$.valid('user-email', valid)
		if (!valid) return
	} else {
		$.valid('user-email')
	}

	const res = await mutate.users.email(username, email)

	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	$('user-email').value = res.email
	const id = `icon-user-email`
	$.show(id)
	setTimeout(() => {
		$.hide(id, true)
	}, 500)
}

export async function show_sessions_info() {
	await _.modal({
		type: 'info',
		title: 'What is a session?',
		text: await api.snippit('login_sessions'),
		buttons: ['OK'],
	}).catch(() => { })
}

export async function show_group_tooltip() {
	await _.modal({
		type: 'info',
		title: 'What are user groups?',
		text: await api.snippit('user_groups'),
		buttons: ['OK'],
	}).catch(() => { })
}

export async function enable_push_notifs() {
	$('enable-push').disabled = true
	if (!push.subscribed) {
		await push.enable().then(push.register).then(push.subscribe)
		push.show_notifs()
	}
	else {
		await push.unsubscribe()
	}

	$('enable-push').checked = push.subscribed
	$('enable-push').disabled = false
	$.blink('icon-notif')
}

export async function show_notifications_info() {
	const res = await _.modal({
		type: 'info',
		title: 'Why enable notifications?',
		text: await api.snippit('notifications'),
		buttons: ['OK', 'More Info'],
	}).catch(() => 'ok')

	if (res === 'ok') return

	dashnav('help/notifications')
}

export async function export_data(username) {
	//Double check with user
	const choice = await _.modal({
		type: 'question',
		title: 'Export all user data?',
		text: 'This will create a ZIP file containing a database export of all user data for user "' + username + '", which will then download to your device.',
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await api(`mutation ($username: String!) {
		exportUserData(username: $username) {
			__typename
			...on Blob { id name ext }
			...on BadTagQuery { message }
			...on UserDoesNotExistError { message }
			...on InsufficientPerms { message }
			...on BlobDoesNotExistError { message }
		}
	}`, {
		username: username,
	})

	if (res.__typename !== 'Blob') {
		_.modal.error(res.message)
		return
	}

	//Download user data
	let link = document.createElement('a')
	link.download = `${res.name}${res.ext}`
	link.href = `/download/${res.id}${res.ext}`
	link.target = '_blank'
	link.click()
}