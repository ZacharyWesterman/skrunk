_('userlist', api('{listUsers}')) //initial load of user list

const Perms = [
	'admin',
	'adult',
]

var UserData = {}

window.revoke_sessions = async function(username)
{
	const choice = await _.modal({
		title: 'Revoke User Sessions',
		text: 'Are you sure you want to revoke all sessions for user "' + username + '"? This will log them out.',
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	await api(`mutation($username: String!){revokeSessions(username: $username)}`, {username: username})
	const session_ct = await api(`query($username: String!){countSessions(username: $username)}`, {username: username})
	$('session-ct-' + username).innerText = session_ct
}

window.load_user_data = async function(username)
{
	$.hide('mainpage')

	UserData = await get_user_data(username)
	const session_ct = await api(`query($username: String!){countSessions(username: $username)}`, {username: username})

	await _('userdata', {
		perms: Perms,
		user: UserData,
		sessions: session_ct,
	})
}

window.hide_user_data = async function()
{
	$.hide('userdata')
	$.show('mainpage')
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

window.confirm_delete_user = async function(username)
{
	var choice = await _.modal({
		title: 'Delete Credentials',
		text: 'Are you sure you want to delete the login for user "' + username + '"? This action cannot be undone!',
		buttons: ['Yes', 'No']
	}).catch(() => 'no')

	if (choice !== 'yes') return

	delete_user(username)
	hide_user_data()
}

var delete_user = async function(username)
{
	const query = `
	mutation ($username: String!){
		deleteUser(username: $username) {
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
		'username' : username,
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

	_('userlist', api('{listUsers}')) //refresh user list
}

window.create_user = async function()
{
	const query = `
	mutation ($username: String!, $password: String!){
		createUser(username: $username, password: $password) {
			__typename
			...on BadUserNameError {
				message
			}
			...on UserExistsError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`
	const vars = {
		'username' : $.val('username'),
		'password' : await api.hash($.val('password')),
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

	$('username').value = ''
	$('password').value = ''

	_('userlist', api('{listUsers}')) //refresh user list
}

$.on.enter($('username'), $.next)
$.on.enter($('password'), create_user)
