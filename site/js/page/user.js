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
