import { load_user_data } from '/js/page/user.js'
await mutate.require('users')
await query.require('users')

export function init() {
	refresh_user_groups()
	refresh_users()
	$.on.enter($('password'), create_user)
}

export async function confirm_delete_user(username) {
	let choice = await _.modal({
		type: 'question',
		title: 'Delete User?',
		text: 'Do you want to delete the login for user "' + username + '"?<br>This will break any info that references this user!',
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	choice = await _.modal({
		type: 'question',
		title: 'Really Delete User?',
		text: 'Are you sure you want to delete user "' + username + '"?<br>This action is permanent and cannot be undone!',
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	delete_user(username)
	$.hide('userdata', true)
}

function refresh_user_groups() {
	_('user_group_list', {
		id: 'user-group-list',
		items: api('{ getUserGroups }'),
	})
}

async function delete_user(username) {
	const res = await mutate.users.delete(username)
	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(() => { })
		return
	}

	_.modal.checkmark()
	refresh_users()
}

export async function create_user() {
	const groups = $.val('user-group-list').split(',').map(i => i.trim()).filter(i => i.length > 0)

	const res = await mutate.users.create(
		$.val('username'),
		await api.hash($.val('password')),
		groups
	)
	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(() => { })
		return
	}

	_.modal.checkmark()
	load_user_data($.val('username'))

	$('username').value = ''
	$('password').value = ''
	$.toggle_expand('card-create')

	refresh_users()
	refresh_user_groups()
}

function refresh_users() {
	_('dropdown', {
		id: 'userlist',
		options: query.users.list(null, false, false), //Don't cache user list, and don't restrict to our group.
		default: 'Select User',
		class: 'big',
	}).then(() => {
		$('userlist').onchange = () => {
			const user = $.val('userlist')
			if (user === '')
				$.hide('userdata', true)
			else
				load_user_data(user)
		}
	})
}

export async function send_test_notification(username) {
	const choice = await _.modal({
		type: 'question',
		title: 'Send Test Notification?',
		text: "This will send the user a test notification, which will appear on their device as a push notification, if they have the feature enabled.<br>This can't be un-sent!",
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	await push.send('Test Notification', 'This is just a test notification. No action is required.', username)
	if (username === api.username) {
		await push.show_notifs()
	}

	_.modal.checkmark()
}
