await mutate.require('documents')
await query.require('documents')

export async function init() {
	await load_documents()
}

export async function new_document() {
	const data = await _.modal({
		title: "New Document",
		text: api.snippit("wiki_edit_document"),
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

	const res = await mutate.documents.create(data.title, data.body)

	if (res.__typename !== 'Document') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()

	load_documents()
}

export async function edit_document(id) {
	const data_promise = api(`query ($id: String!) {
		getDocument (id: $id) {
			__typename
			...on Document { title body }
			...on InsufficientPerms { message }
			...on DocumentDoesNotExistError { message }
		}
	}`, {
		id: id,
	})

	const data = await _.modal({
		title: "Edit Document",
		text: api.snippit("wiki_edit_document"),
		buttons: ["OK", "Cancel"],
	}, async () => {
		// Pull in data on load

		const title = $('title')
		const body = $('body')

		title.disabled = true
		body.disabled = true

		const old_data = await data_promise
		if (old_data.__typename === 'Document') {
			title.value = old_data.title
			body.value = old_data.body
		}

		title.disabled = false
		body.disabled = false
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

	const new_data = await mutate.documents.update(id, data.title, data.body)

	if (new_data.__typename !== 'Document') {
		_.modal.error(new_data.message)
		return
	}

	_.modal.checkmark()

	_(id, new_data)
}


export async function load_documents() {
	const docs = await query.documents.list(0, 100)

	const text = docs.map(doc => `<div id="${doc.id}" template="wiki-doc"></div>`).join('')
	$('document-list').innerHTML = text

	for (const doc of docs) {
		_(doc.id, doc)
	}
}

export async function load_doc_body(id) {
	const field = $(`body-${id}`)

	if (field.loaded) return
	field.loaded = true

	const doc = await query.documents.get_body(id)

	if (doc.__typename !== 'Document') {
		_.modal.error(doc.message)
		return
	}

	field.innerHTML = doc.body_html
}

export async function delete_document(id) {
	const choice = await _.modal({
		title: 'Delete Document?',
		type: 'question',
		text: "Are you sure you want to delete this document?",
		buttons: ['Yes', 'No'],
	})

	if (choice !== 'yes') {
		return
	}

	const choice2 = await _.modal({
		title: 'Really Delete Document?',
		type: 'warning',
		text: `
			Are you <b>really</b> sure you want to delete this document?
			<div class="emphasis">Deletion is permanent and cannot be undone!</div>
			If you just want to prevent others from seeing the document, you may hide it instead.
		`,
		buttons: ['Cancel', 'Yes, Delete'],
	})

	if (choice2 !== 'yes, delete') {
		return
	}

	const res = await mutate.documents.delete(id)

	if (res.__typename !== 'Document') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()
	load_documents()
}
