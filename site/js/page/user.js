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
			$('enable-push').checked = false
			if (push.subscribed) {
				try {
					const auth = JSON.parse(JSON.stringify(push.subscription)).keys.auth
					if (auth) {
						api(`query ($auth: String!) { getSubscription(auth: $auth) { __typename } }`, {
							auth: auth,
						}).then(sub => {
							if (sub && sub.__typename === 'Subscription') {
								$('enable-push').checked = true
							}
						})
					}
				} catch (e) {
					console.warn('Error checking push subscription:', e)
				}
			}
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

function password_strength(password) {
	if (password.length < 8) return 0 //very weak
	if (password.includes(api.username)) return 0 //very weak
	if (api.username.includes(password)) return 0 //very weak

	const has_upper = /[A-Z]/.test(password)
	const has_lower = /[a-z]/.test(password)
	const has_number = /[0-9]/.test(password)
	const has_symbol = /[!@#$%^&*(),.?":{}|<>]/.test(password)

	const long_password = password.length >= 12 ? 1 : 0

	const score = has_upper + has_lower + has_number + has_symbol + long_password
	return score
}

function is_valid_password(password) {
	if (password.length < 8) return false
	if (password.includes(api.username)) return false
	if (api.username.includes(password)) return false

	const has_upper = /[A-Z]/.test(password)
	const has_lower = /[a-z]/.test(password)
	const has_number = /[0-9]/.test(password)
	const has_symbol = /[!@#$%^&*(),.?":{}|<>]/.test(password)

	if (has_upper + has_lower + has_number + has_symbol < 2) return false

	return true
}

export function check_password() {
	const password = $.val('user-new-password')

	const criteria = {
		'pw1': password.length >= 8,
		'pw2': !password.includes(api.username) && password.length > 0,
		'pw3': !api.username.includes(password) && password.length > 0,
		'pw5': /[A-Z]/.test(password),
		'pw6': /[a-z]/.test(password),
		'pw7': /[0-9]/.test(password),
		'pw8': /[!@#$%^&*(),.?":{}|<>]/.test(password),
	}
	criteria.pw4 = (criteria.pw5 + criteria.pw6 + criteria.pw7 + criteria.pw8) >= 2

	for (const [key, valid] of Object.entries(criteria)) {
		$(key).style.textDecoration = valid ? 'line-through' : ''
		$(key).classList.toggle('suppress', valid)
	}

	const score = [
		'Very Weak',
		'Weak',
		'Fair',
		'Good',
		'Strong',
		'Very Strong',
	][password_strength(password)]
	$('password-strength').innerText = score
}

export function bind_password() {
	$.bind('user-new-password', check_password, 10)
}

export function expand_password_hints() {
	$.toggle_expand('password-hints', true)
	$.show('password-strength')
}

export function contract_password_hints() {
	$.toggle_expand('password-hints', false)
	$.hide('password-strength', true)
}

export async function update_password(password, username) {
	if (password.length === 0) {
		//Just flash the password field
		$.flash('user-new-password')
		$.flash('user-new-password2')
		return
	}

	if (!is_valid_password(password)) {
		const criteria = [
			'Must be at least 8 characters long',
			'Must not contain your username, nor be a subset of your username',
			'Must contain at least 2 of the following: uppercase, lowercase, number, symbol',
		]

		_.modal({
			type: 'error',
			title: 'Invalid Password',
			text: 'Password must fit <i>all</i> of the following criteria:<ul><li>' + criteria.join('</li><li>') + '</li></ul>',
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	//Hide the password hints and score, since the password is valid
	contract_password_hints()

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

	//Wipe password fields
	$('user-new-password').value = ''
	$('user-new-password2').value = ''
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

		//If user is trying to subscribe, but the browser did not allow it for some reason,
		//Show an error message and give the user the option to troubleshoot.
		if (!push.subscribed) {
			$('enable-push').checked = push.subscribed
			$('enable-push').disabled = false

			const choice = await _.modal({
				type: 'error',
				title: 'Cannot Enable Notifications',
				text: `Push notification permission was not granted to this website.<br><br>
				Normally this means that either the user has manually denied notifications for this site,
				or the feature is not enabled in the first place.<br><br>
				For help enabling this feature on iOS, Android, or PC, click the <i>Help</i> button.
				If you still can't enable notifications after following the instructions,
				then your browser may not support push notifications.`,
				buttons: ['OK', 'Help'],
			})

			if (choice === 'help') {
				dashnav('help/enable_notifications')
			}

			return
		}
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
		text: `This will create a ZIP file containing a database dump of all user data for <span class="emphasis">${username}</span>, which will then download to your device.
		<br>This will <b>not</b> include any uploaded files; those must be downloaded separately.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	_.modal({
		text: api.snippit('export-waiting'),
		buttons: [],
		no_cancel: true,
	})

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

	_.modal.return()

	//Download user data
	let link = document.createElement('a')
	link.download = `${res.name}${res.ext}`
	link.href = `/download/${res.id}${res.ext}`
	link.target = '_blank'
	link.click()
}

export async function change_username(username) {
	async function username_check() {
		const newvalue = $.val('username')
		const message = $('username-message')

		if (newvalue === username || newvalue === '') {
			$.valid('username')
			message.innerText = 'Username is unchanged.'
			return false
		}

		const res = await query.users.get(newvalue)
		if (res.__typename === 'UserData') {
			$.invalid('username')
			message.innerText = 'Username is not available.'
			return false
		}
		else if (res.__typename !== 'UserDoesNotExistError') {
			$.invalid('username')
			message.innerText = 'ERROR: ' + res.message
			return false
		}

		$.valid('username')
		message.innerText = 'Username is available.'
		return true
	}

	const newvalue = await _.modal({
		icon: 'pen-to-square',
		title: 'Change Username',
		text: `<p>
			If the new username is available, this will immediately update your <u>username</u> everywhere.
			This will not affect your <u>Display Name</u>.<br>
			<b class="emphasis">Changing your username will log you out of all devices.</b>
		</p>
		&nbsp;<input id="username" placeholder="Username" format="id" value="${username}" />
		&nbsp;<div id="username-message">&nbsp;</div>`,
		buttons: ['Submit', 'Cancel'],
	}, () => {
		//When user edits username, automatically check if it's available.
		$.bind('username', username_check)
	}, async choice => {
		if (choice === 'cancel') return true
		return await username_check()
	},
		choice => (choice === 'cancel') ? null : $.val('username')
	).catch(() => null)

	if (newvalue === null) return

	//User has elected to change their username. Perform that action.
	const res = await api(`mutation ($username: String!, $newvalue: String!) {
		updateUsername (username: $username, newvalue: $newvalue) {
			__typename
			...on UserDoesNotExistError { message }
			...on UserExistsError { message }
			...on BadUserNameError { message }
			...on InsufficientPerms { message }
		}
	}`, {
		username: username,
		newvalue: newvalue,
	})

	if (res.__typename !== 'UserData') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()

	if (username === api.username) {
		//Now that username is updated, request a new login token.
		// await api.refresh_token(newvalue)
		//Login token refresh doesn't really work when username changes... Just logout instead.
		setTimeout(api.logout, 700)
	}
}
