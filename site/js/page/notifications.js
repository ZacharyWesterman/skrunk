let CurrentPage = 0
const LookupListLen = 15

export async function init() {
	await _('lookup', {
		template: 'notifications',
		fields: `
		<button class="button alt big border clickable" *click="mark_all_notifs_as_read">
			Mark All as Read
		</button>
		<hr/>
		`,
	})
	navigate_to_page(0)
}

async function read_notifs(start, count) {
	//Get notification list (unread only)
	return api(`query ($username: String!, $read: Boolean!, $start: Int!, $count: Int!) {
		getNotifications (username: $username, read: $read, start: $start, count: $count) {
			recipient
			created
			message
			category
			id
		}
	}`, {
		username: api.username,
		read: false,
		start: start,
		count: count,
	}).then(notifs => notifs.map(i => {
		const msg = JSON.parse(i.message)
		i.title = msg.title
		i.body = msg.body
		return i
	}))
}

async function refresh_page_list() {
	const lookup_start = CurrentPage * LookupListLen

	//Get notification count (unread only)
	const counts = await (api(`query ($username: String!, $read: Boolean!) { countNotifications(username: $username, read: $read) }`, {
		username: api.username,
		read: false,
	}).then(count => {
		const page_ct = Math.ceil(count / LookupListLen)
		const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
		return {
			pages: pages,
			count: page_ct,
			current: Math.floor(lookup_start / LookupListLen),
			total: count,
		}
	}))

	await _('page-list', counts, true)
}

export async function navigate_to_page(page_num) {
	push.show_notifs()

	const lookup_start = page_num * LookupListLen
	CurrentPage = page_num

	//Get notification list (unread only)
	const items_promise = read_notifs(lookup_start, LookupListLen)
	refresh_page_list()

	await _('lookup-results', items_promise)

	for (const i of $('notif', true)) {
		i.onclick = () => mark_as_read(i.id)
	}
}

export async function mark_as_read(id) {
	await api(`mutation ($id: String!) {
		markNotifAsRead (id: $id)
	}`, {
		id: id,
	})

	// Remove ONLY the notification that was marked as read.
	await $.hide(id, true)
	$(id).remove();

	// Fetch another notification, and add it to the list.
	const items = await read_notifs((CurrentPage + 1) * LookupListLen - 1, 1)
	if (items.length) {
		const parent = document.createElement('div');
		parent.setAttribute('template', 'notifications')

		await _(parent, items, true)
		const child = parent.children[0]
		$('lookup-results').appendChild(child)
		child.onclick = () => mark_as_read(child.id)
	}

	refresh_page_list()
	push.show_notifs()
}

export async function mark_all_notifs_as_read() {
	const ct = await api(`query ($username: String!, $read: Boolean!) {
		countNotifications (username: $username, read: $read)
	}`, {
		username: api.username,
		read: false,
	})
	const res = await _.modal({
		type: 'question',
		title: 'Mark All as Read?',
		text: `This will update <b>${ct}</b> notifications and hide them from view.<br>Continue?`,
		buttons: ['Yes', 'No'],
	})

	if (res !== 'yes') return

	await api(`mutation ($username: String!) {
		markAllNotifsAsRead (username: $username)
	}`, {
		username: api.username,
	})

	_.modal.checkmark()
	navigate_to_page(0)
}
