window.get_user_data = async function(username)
{
	return await api(`query ($username: String!){
		getUser(username:$username) {
			__typename
			...on UserData {
				username
				theme {
					colors {
						name
						value
					}
					sizes {
						name
						value
					}
				}
				perms
			}
			...on UserDoesNotExistError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`, {username: username})
}

//Load user theme (regardless of cookies)
get_user_data(api.username).then(data => {
	if (data.__typename !== 'UserData')
	{
		//If user data does not exist, we don't want them to have access. Kick them out.
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: data.message,
			buttons: ['OK']
		}).then(() => api.logout()).catch(() => {})
	}

	//Load user colors
	for (var i of data.theme.colors || [])
	{
		_.css.set_var(i.name, i.value)
	}

	//Load user sizes
	for (var i of data.theme.sizes || [])
	{
		_.css.set_var(i.name, i.value)
	}

	//Load navbar based on user perms
	_('navbar', data.perms)
})
