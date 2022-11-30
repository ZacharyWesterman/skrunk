_('userlist', api('{listUsers}')) //initial load of user list

window.delete_user = async function(username)
{
	const query = `
	mutation ($username: String!){
		deleteUser(username: $username) {
			__typename
			...on UserDoesNotExistError {
				message
			}
			...on InsufficientCreds {
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
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
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
			...on InsufficientCreds {
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
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
	}

	_('userlist', api('{listUsers}')) //refresh user list
}
