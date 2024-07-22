export async function init() {
	await _('lookup', {
		header: `
			<span class="clickable" *toggles="data-feed-expand">
				<i id="chevron" class="left fa-solid fa-angles-down"></i>
				My Feeds
			</span>
			<span name="feed-choice-div" template="dropdown"></span>
			<span style="font-size: 80%;" class="tooltip" *click="help">
				<i class="fa-solid fa-circle-question"></i>
				<span class="tooltiptext t-center">What are data feeds?</span>
			</span>`,
		fields: `
			<div id="data-feed-expand" class="expand-container">
				<div name="data_feed_list">Loading your data feeds...</div>
			</div>`,
		template: 'feed_documents',
	})

	await _('feed-choice-div', {
		id: 'feed-choice',
		options: [],
		default: "Loading...",
		append: true,
	})

	await get_my_feeds()

	window.help_types = help_types
	window.unload.push(() => {
		delete window.help_types
	})
}

async function get_my_feeds() {
	const p1 = api.get_json('config/feed_types.json')

	const res = await api(`query ($username: String!) {
		getUserFeeds(username: $username) { id name kind }
	}`, {
		username: api.username,
	}).then(async res => {
		let types = {}
		const t = await p1
		t.forEach(item => { types[item.value] = item })

		res.forEach(item => {
			item.kind = types[item.kind] || { value: item.kind }
		})

		return res
	})

	$.toggle('chevron', res.length > 0, true)
	const dropdown = res.map(item => {
		return {
			value: item.id,
			display: item.name,
		}
	})

	_('data_feed_list', res)

	_('feed-choice-div', {
		id: 'feed-choice',
		options: dropdown,
		default: "No Feed Selected",
		append: true,
	}).then(() => {
		$.bind('feed-choice', () => navigate_to_page(0))
	})
}

export async function append_modal() {
	//Create new feed

	const choice = await _.modal({
		title: 'New Data Feed',
		icon: 'rss',
		text: api.snippit('new_feed'),
		buttons: ['OK', 'Cancel'],
	}, () => {
		//On load
		_('kind', {
			id: 'kind',
			default: false,
			options: api.get_json('config/feed_types.json'),
		})
	}, choice => {
		//Validate
		if (choice !== 'ok') return true

		let valid = true
		for (let i of ['name', 'kind', 'url']) {
			if (!$.val(i)) {
				$.flash(i)
				valid = false
			}
		}

		return valid
	}, choice => {
		//Mutate
		if (choice !== 'ok') return null

		return {
			name: $.val('name'),
			kind: $.val('kind'),
			url: $.val('url'),
			notify: $('notify').checked,
		}
	})

	if (choice === null) return

	//User wants to create a data feed. Not much validation we can do as to the URL and whatnot, so just assume it's correct.
	//If it's incorrect, the user can delete or edit the feed later.
	const res = await api(`mutation ($name: String!, $url: String!, $kind: String!, $notify: Boolean!) {
		createFeed (name: $name, url: $url, kind: $kind, notify: $notify) {
			__typename
			...on UserDoesNotExistError { message }
			...on InsufficientPerms { message }
			...on InvalidFeedKindError { message }
		}
	}`, choice)

	if (res.__typename !== 'Feed') {
		_.modal.error(res.message)
	} else {
		_.modal.checkmark()
		get_my_feeds()
	}
}

export async function delete_feed(id) {
	const choice = await _.modal({
		title: 'Delete data feed?',
		text: 'This action is permanent and will remove any documents related to the feed.<br>Continue to delete it?',
		type: 'question',
		buttons: ['Yes', 'No'],
	})

	if (choice !== 'yes') return

	const res = await api(`mutation ($id: String!) {
		deleteFeed (id: $id) {
			__typename
			...on UserDoesNotExistError { message }
			...on InsufficientPerms { message }
			...on FeedDoesNotExistError { message }
		}
	}`, {
		id: id,
	})

	if (res.__typename !== 'Feed') {
		_.modal.error(res.message)
	} else {
		_.modal.checkmark()
		get_my_feeds()
	}
}

export function help() {

}

export function help_types() {
	const p1 = api.get_json('config/feed_types.json')
	_.modal({
		title: 'Feed types and their meaning',
		type: 'info',
		text: '<div name="feed_types">Loading...</div>',
		buttons: ['OK'],
	}, () => _('feed_types', p1))
}

export async function navigate_to_page(page_num) {
	const lookup_list_len = 15
	const lookup_start = page_num * lookup_list_len

	const count_promise = api(`query ($feed: String!) { countFeedDocuments(feed: $feed) }`, {
		feed: $.val('feed-choice')
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

	const items_promise = api(`query ($feed: String!, $start: Int!, $count: Int!) {
		getFeedDocuments(feed: $feed, start: $start, count: $count) {
			author
			posted
			body
			body_html
			fetched
			updated
		}
	}`, {
		feed: $.val('feed-choice'),
		start: lookup_start,
		count: lookup_list_len,
	})

	_('page-list', count_promise)
	_('lookup-results', items_promise)
}
