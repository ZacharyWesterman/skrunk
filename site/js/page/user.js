await mutate.require('users')
await query.require('users')

let Perms
let UserData = {}

export async function revoke_sessions(username)
{
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

export async function set_perms()
{
	let new_perms = []
	let perms_changed = []
	for (const perm of Perms)
	{
		const checked = $('perm-'+perm.name).checked
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
		}).catch(()=>{})
		return
	}

	for (const perm of perms_changed)
	{
		const id = `icon-perm-${perm}`
		$.show(id)
		setTimeout(() => {
			$.hide(id, true)
		}, 500)
	}

	sync_perm_descs()
}

export async function load_user_data(username, self_view = false)
{
	let p
	if (!Perms)
	{
		p = api.get_json('/config/permissions.json')
	}

	let p2 = api('{ getUserGroups }')

	UserData = await query.users.get(username)
	if (p) Perms = await p

	await _('userdata', {
		perms: Perms,
		user: UserData,
		sessions: query.users.sessions(username),
		self_view: self_view,
	})

	await _('usrgrp', {
		id: 'user-group',
		items: p2,
	})
	$('user-group').value = UserData.groups ? (UserData.groups[0] || '') : ''

	sync_perm_descs()
}

export async function update_groups(username)
{
	const groups = $.val('user-group')

	const res = await api(`mutation ($username: String!, $groups: [String!]!) {
		updateUserGroups (username: $username, groups: $groups) {
			__typename
			...on UserDoesNotExistError { message }
			...on InsufficientPerms { message }
		}
	}`, {
		username: username,
		groups: groups ? [groups] : [],
	})

	if (res.__typename !== 'UserData')
	{
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
		$('user-group').value = groups
	})
}

function sync_perm_descs()
{
	for (const perm of Perms)
	{
		const desc = $('perm-'+perm.name).checked ? "true" : "false"
		$('perm-tooltip-'+perm.name).innerText = perm[desc]
	}
}

export async function update_password(password, username)
{
	if ((password.length < 8) || (password === username) || (password.includes(username) && (password.length < username.length * 2)))
	{
		const criteria = [
			'Must be at least 8 characters long',
			'May not contain the username, unless it\'s at least 2&times; the length',
		]

		_.modal({
			type: 'error',
			title: 'Invalid Password',
			text: 'Password must fit <i>all</i> of the following criteria:<ul><li>' + criteria.join('</li><li>') + '</li></ul>',
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	if (password !== $.val('user-new-password2'))
	{
		_.modal({
			type: 'error',
			title: 'Passwords don\'t match',
			text: 'Make sure you typed the password in correctly!',
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	const hashed_pass = await api.hash(password)
	const res = await mutate.users.password(username, hashed_pass)

	if (res.__typename !== 'UserData')
	{
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

export async function update_user_display_name(username)
{
	const display_name = $.val('user-display-name')
	const res = await mutate.users.display_name(username, display_name)

	if (res.__typename !== 'UserData')
	{
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

export async function show_sessions_info()
{
	await _.modal({
		type: 'info',
		title: 'What is a session?',
		text: await api.get('/html/snippit/login_sessions.html'),
		buttons: ['OK'],
	}).catch(() => {})
}
