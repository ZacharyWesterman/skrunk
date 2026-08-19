await mutate.require('documents')
await query.require('documents')

function generate_id() {
	var d = new Date().getTime();
	var d2 = (performance !== undefined && performance.now && (performance.now() * 1000)) || 0;
	return 'xxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
		var r = Math.random() * 10;//random number between 0 and 10
		if (d > 0) {//Use timestamp until depleted
			r = (d + r) % 10 | 0;
			d = Math.floor(d / 10);
		} else {//Use microseconds since page-load if supported
			r = (d2 + r) % 10 | 0;
			d2 = Math.floor(d2 / 10);
		}
		return r;
	});
}

window.wopi = {
	url: api(`{ getConfig(name: "wopi:url") }`),
	reverse: api(`{ getConfig(name: "wopi:reverse_url") }`),
	id: generate_id(),
	supported: false,
}

export async function init() {
	for (const i in wopi) {
		wopi[i] = await wopi[i]
	}
	wopi.supported = wopi.url !== '' && wopi.reverse !== ''

	await load_documents()
}

export async function new_document() {
	const data = await _.modal({
		title: "New Document",
		text: wopi.supported ? '<input type="text" id="title" placeholder="Document Title" />' : api.snippit("edit-document"),
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
			body: $.val('body') ?? '',
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

	if (wopi.supported) {
		edit_document(res.id)
	}
}

export async function edit_document(id) {
	if (wopi.supported) {
		const jwt = api.login_token.split(' ')[1]
		const url = `${wopi.url}/browser/${wopi.id}/cool.html?WOPISrc=${wopi.reverse}/${jwt}/wopi/files/${id}`

		//On desktop, open view in-browser.
		const elem = $('pdf-viewer')
		elem.innerHTML = `
		<iframe frameborder="0" style="width: 100%; height: 100%;" src="${url}" allow="clipboard-read *; clipboard-write *; fullscreen *"></iframe>
		<div class="clickable close-pdf-viewer">
			<i style="position: relative; top:15%;" class="fa-solid fa-times fa-lg"></i>
		</div>
		`

		const exit_pdf_viewer = async () => {
			$.on.detach.escape(window)
			await $.hide('pdf-viewer', true)
			$('pdf-viewer').innerHTML = ''
		}

		$.on.escape(window, exit_pdf_viewer)
		elem.children[1].onclick = exit_pdf_viewer

		$.show(elem)
		elem.style.display = 'block'

		return
	}

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
		text: api.snippit("edit-document"),
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

	const text = docs.map(doc => `<div id="${doc.id}" template="document-stub"></div>`).join('')
	$('document-list').innerHTML = text

	for (const doc of docs) {
		_(doc.id, doc)
	}

	console.log(docs)
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
	}).catch(() => 'no')

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
	}).catch(() => 'cancel')

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


export async function view_document(id) {
	if (!wopi.supported) {
		await _.modal({
			text: `<br><div id="body-${id}">Loading...</div>`,
			buttons: ['OK'],
		}, () => load_doc_body(id)).catch(() => { })
		return
	}

	const jwt = api.login_token.split(' ')[1]
	const url = `${wopi.url}/browser/${wopi.id}/cool.html?WOPISrc=${wopi.reverse}/${jwt}/wopi/files/${id}`

	//On desktop, open view in-browser.
	const elem = $('pdf-viewer')
	elem.innerHTML = `
	<iframe frameborder="0" style="width: 100%; height: 100%;" src="${url}" allow="fullscreen *"></iframe>
	<div class="clickable close-pdf-viewer">
		<i style="position: relative; top:15%;" class="fa-solid fa-times fa-lg"></i>
	</div>
	`

	const exit_pdf_viewer = async () => {
		$.on.detach.escape(window)
		await $.hide('pdf-viewer', true)
		$('pdf-viewer').innerHTML = ''
	}

	$.on.escape(window, exit_pdf_viewer)
	elem.children[1].onclick = exit_pdf_viewer

	$.show(elem)
	elem.style.display = 'block'
}
