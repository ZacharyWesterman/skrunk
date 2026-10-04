let LookupStart = 0
let LookupListLen = 15
let CurrentPage = 0

export async function init() {
	navigate_to_page(0)
}

export async function navigate_to_page(page_num) {
	CurrentPage = page_num

	const filter = {
		category: $.val('category') || null,
		type: $.val('type') || null,
		location: $.val('location') || null,
		owner: $.val('owner') || null,
	}

	const count_promise = api('{countMotd}').then(res => {
		const count = res

		const page_ct = Math.ceil(count / LookupListLen)
		const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
		let this_page = Math.floor(LookupStart / LookupListLen)
		if (page_ct === 0) {
			this_page = LookupStart = 0
		}
		else if (this_page >= page_ct) {
			this_page = page_ct - 1
			LookupStart = this_page * LookupListLen
		}

		return {
			pages: pages,
			count: page_ct,
			current: this_page,
			total: count,
		}
	})

	const items_promise = api(`query ($start: Int!, $count: Int!) {
		listMotd(start: $start, count: $count) {
			id
			text
			text_html
			created
		}
	}`, {
		start: LookupStart,
		count: LookupListLen,
	})

	await _('page-list', count_promise)
	await _('lookup-results', items_promise)
}

export async function create_motd() {
	const choice = await _.modal({
		title: 'Create new MOTD',
		text: '<input type="richtext" id="motd-text" />',
		buttons: ['OK', 'Cancel'],
	}, undefined, undefined, choice => {
		return choice !== 'cancel' ? ($.val('motd-text') || null) : null
	}).catch(() => null)

	if (choice === null) {
		return
	}

	const res = await api(`mutation ($text: String!) {
		createMotd (text: $text) {
			__typename
			...on InsufficientPerms { message }
		}
	}`, {
		text: choice,
	})

	if (res.__typename !== 'Motd') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()
	navigate_to_page(0)
}

export async function edit_motd(id, text) {
	const choice = await _.modal({
		title: 'Edit MOTD',
		text: '<input type="richtext" id="motd-text" />',
		buttons: ['OK', 'Cancel'],
	}, () => {
		$.set('motd-text', text)
	}, undefined, choice => {
		return choice !== 'cancel' ? ($.val('motd-text') || null) : null
	}).catch(() => null)

	if (choice === null) {
		return
	}

	const res = await api(`mutation ($id: String!, $text: String!) {
		updateMotd (id: $id, text: $text) {
			__typename
			...on InsufficientPerms { message }
			...on MotdDoesNotExist { message }
		}
	}`, {
		id,
		text: choice,
	})

	if (res.__typename !== 'Motd') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()
	navigate_to_page(CurrentPage)
}

export async function delete_motd(id) {
	const choice = await _.modal({
		type: 'warning',
		title: 'Delete MOTD?',
		text: 'This action cannot be undone!',
		buttons: ['Yes', 'No'],
	})

	if (choice !== 'yes') {
		return
	}

	const res = await api(`mutation ($id: String!) {
		deleteMotd (id: $id) {
			__typename
			...on InsufficientPerms { message }
			...on MotdDoesNotExist { message }
		}
	}`, {
		id,
	})

	if (res.__typename !== 'Motd') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()
	navigate_to_page(CurrentPage)
}
