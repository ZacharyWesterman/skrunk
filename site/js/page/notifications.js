let CurrentPage = 0

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

export async function navigate_to_page(page_num, update_nav = true) {
	push.show_notifs()

	const lookup_list_len = 15
	const lookup_start = page_num * lookup_list_len

	CurrentPage = page_num

	//Get notification count (unread only)
	const count_promise = api(`query ($username: String!, $read: Boolean!) { countNotifications(username: $username, read: $read) }`, {
		username: api.username,
		read: false,
	}).then(count => {
		const page_ct = Math.ceil(count / lookup_list_len)
		const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
		return {
			pages: pages,
			count: page_ct,
			current: Math.floor(lookup_start / lookup_list_len),
			total: count,
		}
	})

	//Get notification list (unread only)
	const items_promise = api(`query ($username: String!, $read: Boolean!, $start: Int!, $count: Int!) {
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
		start: lookup_start,
		count: lookup_list_len,
	}).then(notifs => notifs.map(i => {
		const msg = JSON.parse(i.message)
		i.title = msg.title
		i.body = msg.body
		return i
	}))

	await _('lookup-results', items_promise)
	await _('page-list', count_promise)
}

export async function mark_as_read(id) {
	await api(`mutation ($id: String!) {
        markNotifAsRead (id: $id)
    }`, {
		id: id,
	})

	navigate_to_page(CurrentPage)
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