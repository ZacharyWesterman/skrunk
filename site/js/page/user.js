const Perms = [
	'admin',
	'adult',
]

var UserData = {}

window.revoke_sessions = async function(username)
{
	if (username === api.username)
		msg = 'Are you sure you want to revoke your sessions? This will log you out of all devices, including this one.'
	else
		msg = 'Are you sure you want to revoke all sessions for user "' + username + '"? This will log them out.'

	const choice = await _.modal({
		title: 'Revoke User Sessions',
		text: msg,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	await api(`mutation($username: String!){revokeSessions(username: $username)}`, {username: username})
	const session_ct = await api(`query($username: String!){countSessions(username: $username)}`, {username: username})
	$('session-ct-' + username).innerText = session_ct
}

window.set_perms = async function()
{
	UserData.perms = []
	for (var perm of Perms)
	{
		if ($('perm-'+perm).checked) UserData.perms.push(perm)
	}

	const query = `
	mutation ($username: String!, $perms: [String!]!){
		updateUserPerms(username: $username, perms: $perms) {
			__typename
			...on UserDoesNotExistError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`
	const vars = {
		'username' : UserData.username,
		'perms': UserData.perms,
	}
	var res = await api(query, vars)
	if (res.__typename !== 'UserData') {
		_.modal({
			title: '<span class="error">ERROR</span>',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
		return
	}
}

window.load_user_data = async function(username, self_view = false)
{
	$.hide('mainpage')

	UserData = await get_user_data(username)
	const session_ct = await api(`query($username: String!){countSessions(username: $username)}`, {username: username})

	await _('userdata', {
		perms: Perms,
		user: UserData,
		sessions: session_ct,
		self_view: self_view,
	})
}

window.update_password = async function(password, username)
{
	if ((password.length < 8) || (password === username) || (password.includes(username) && (password.length < username.length * 2)))
	{
		const criteria = [
			'Must be at least 8 characters long',
			'May not contain the username, unless it\'s at least 2&times; the length',
		]

		_.modal({
			title: '<span class="error">Invalid Password</span>',
			text: 'Password must fit <i>all</i> of the following criteria:<ul><li>' + criteria.join('</li><li>') + '</li></ul>',
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	const hashed_pass = await api.hash(password)
	const res = await api(`mutation ($username: String!, $password: String!) {
		updateUserPassword(username: $username, password: $password) {
			__typename
			...on UserDoesNotExistError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`, {
		username: username,
		password: hashed_pass,
	})

	if (res.__typename !== 'UserData')
	{
		_.modal({
			title: '<span class="error">ERROR</span>',
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

window.show_sessions_info = async () => {
	await _.modal({
		title: 'What is a session?',
		text: await api.get('/html/snippit/login_sessions.html'),
		buttons: ['OK'],
	}).catch(() => {})
}

window.unload.push(() => {
	delete window.load_user_data
	delete window.set_perms
	delete window.revoke_sessions
	delete window.update_password
	delete window.show_sessions_info
})
