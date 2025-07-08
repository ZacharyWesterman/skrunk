export async function init() {
	await load_documents()

	//Load content of top-level documents
	for (const elem of document.getElementsByName('document-body')) {
		load_doc_body(elem.id)
	}
}

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
	}).catch(() => null)

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

	await load_documents(parent_id)

	if (!parent_id) {
		//Load content of top-level documents
		for (const elem of document.getElementsByName('document-body')) {
			load_doc_body(elem.id)
		}
	}
}

export async function load_documents(parent_id) {
	const docs = await api(`query ($parent: String) {
		getChildDocuments (id: $parent) {
			id
			title
			creator {
				username
				display_name
			}
			created
		}
	}`, {
		parent: parent_id || null,
	})

	const element = parent_id ? `child-docs-${parent_id}` : 'top-level-docs'
	await _(element, {
		docs: docs,
		toplevel: !parent_id,
	})
}

export async function load_doc_body(id) {
	if ($(id).loaded) return
	$(id).loaded = true

	const doc = await api(`query ($id: String!) {
		getDocument (id: $id) {
			__typename
			...on Document { body_html }
			...on InsufficientPerms { message }
			...on DocumentDoesNotExistError { message }
		}
	}`, {
		id: id,
	})

	if (doc.__typename !== 'Document') {
		_.modal.error(doc.message)
		return
	}

	$(id).innerHTML = doc.body_html

	//Load child documents
	load_documents(id)
}
