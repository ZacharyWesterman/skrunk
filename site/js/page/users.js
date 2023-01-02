export function init()
{
	_('userlist', query.users.list()) //initial load of user list
	$.on.enter($('password'), create_user)
}

export async function hide_user_data()
{
	$.hide('userdata')
	$.show('mainpage')
}

export async function confirm_delete_user(username)
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
	var res = await mutate.users.delete(username)
	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
		return
	}

	_('userlist', query.users.list()) //refresh user list
}

export async function create_user()
{
	var res = await mutate.users.create(
		$.val('username'),
		await api.hash($.val('password'))
	)
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

	_('userlist', query.users.list()) //refresh user list
}
