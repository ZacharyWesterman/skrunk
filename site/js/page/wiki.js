export async function new_document(parent_id) {
	const data = await _.modal({
		title: "New Document",
		text: api.snippit("wiki_new_document"),
		buttons: ["OK", "Cancel"],
	}, () => {
		//On load
	}, choice => {
		//Validate input

		if (choice === 'ok' && !$.val('title')) {
			$.flash('title')
			return false
		}

		return true
	}, choice => {
		//Transform input
		if (choice === 'cancel') return null

		return {
			title: $.val('title'),
			body: $.val('body'),
		}
	})

	if (!data) return

	const res = await api(`mutation ($title: String!, $body: String!, $parent: String) {
		createDocument (title: $title, body: $body, parent: $parent) {
			__typename
			...on InsufficientPerms { message }
			...on DocumentDoesNotExistError { message }
		}
	}`, {
		title: data.title,
		body: data.body,
		parent: parent_id || null,
	})

	if (res.__typename !== 'Document') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()
}
