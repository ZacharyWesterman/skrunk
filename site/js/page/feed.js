export async function init() {
	const user_feeds = api(`query ($username: String!) {
		getUserFeeds(username: $username) { id name }
	}`, {
		username: api.username,
	}).then(res => {
		$.toggle('chevron', res.length > 0, true)

		return res.map(item => {
			return {
				value: item.id,
				display: item.name,
			}
		})
	})

	_('feed-choice', {
		id: 'feed-choice',
		options: user_feeds,
		default: "No Feed Selected",
		append: true,
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
	}
}
