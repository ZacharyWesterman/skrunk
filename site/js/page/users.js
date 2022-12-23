_('userlist', api('{listUsers}')) //initial load of user list

window.hide_user_data = async function()
{
	$.hide('userdata')
	$.show('mainpage')
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
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
		return
	}

	_('userlist', api('{listUsers}')) //refresh user list
}

export async function create_user()
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
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
		return
	}

	$('username').value = ''
	$('password').value = ''

	_('userlist', api('{listUsers}')) //refresh user list
}

$.on.enter($('password'), create_user)

window.unload.push(() => {
	delete window.hide_user_data
	delete window.confirm_delete_user
	delete window.create_user
})
