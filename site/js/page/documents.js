await mutate.require('documents')
await query.require('documents')

let DocStart = 0
let DocListLen = 15

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
	url: null,
	reverse: null,
	id: generate_id(),
	supported: false,
}

export async function init() {
	wopi.url = await api(`{ getConfig(name: "wopi:url") }`).then(i => i ? i.replace('{}', window.location.href.split(/(?<!\/)[\/:](?!\/)/, 1)) : null)
	wopi.reverse = await api(`{ getConfig(name: "wopi:reverse_url") }`).then(i => i ? i.replace('{}', window.location.href.split(/(?<!\/)[\/:](?!\/)/, 1)) : null)
	wopi.supported = (wopi.url ?? '') !== '' && (wopi.reverse ?? '') !== ''

	if (wopi.supported) {
		$.show('import-button', false)
	}

	await navigate_to_page(0)
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

	const res = await (wopi.supported ?
		mutate.documents.create_blob(data.title) :
		mutate.documents.create(data.title, data.body)
	)

	if (res.__typename !== 'Document') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()

	if (wopi.supported) {
		wopi_edit_document(res.id)
	}

	await load_documents()
	await reload_page_list()
}

function get_wopi_url(id) {
	const jwt = api.login_token.split(' ')[1]
	const url = `${wopi.url}/browser/${wopi.id}/cool.html?WOPISrc=${wopi.reverse}/${jwt}/wopi/files/${id}`
	return url
}

export async function wopi_edit_document(id) {
	//On desktop, open view in-browser.
	const elem = $('pdf-viewer')
	elem.innerHTML = `
	<iframe frameborder="0" style="width: 100%; height: 100%;" src="${get_wopi_url(id)}" allow="fullscreen *"></iframe>
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

export async function view_document_new_tab(id) {
	open(get_wopi_url(id), '_blank')
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
		title: "Edit Document" + (wopi.supported ? ' Title' : ''),
		text: wopi.supported ? '<input type="text" id="title" placeholder="Document Title" />' : api.snippit("edit-document"),
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
			body: wopi.supported ? null : $.val('body'),
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
	const filter = {
		tag_expr: $.val('tag-query') || null,
		title: $.val('filter-title') || null,
	}

	const res = await query.documents.list(filter, DocStart, DocListLen)

	$('tag-error').innerText = res.message || ''
	if (res.__typename !== 'DocumentList') {
		return
	}

	const docs = res.documents
	const text = docs.map(doc => `<div id="${doc.id}" template="document-stub"></div>`).join('')
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
		title: 'Really Delete Document?',
		type: 'warning',
		text: `
			Are you <b>really</b> sure you want to delete this document?
			<div class="emphasis">Deletion is permanent and cannot be undone!</div>
		`,
		buttons: ['Cancel', 'Yes, Delete'],
	}).catch(() => 'cancel')

	if (choice !== 'yes, delete') {
		return
	}

	const res = await mutate.documents.delete(id)

	if (res.__typename !== 'Document') {
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()
	reload_page_list()
	load_documents()

	if (wopi.supported) {
		$.toggle_expand('delete-helper', true)
	}
}


export async function view_document(id) {
	if (wopi.supported) {
		wopi_edit_document(id)
		return
	}

	await _.modal({
		text: `<br><div id="body-${id}">Loading...</div>`,
		buttons: ['OK'],
	}, () => load_doc_body(id)).catch(() => { })
	return
}


export async function navigate_to_page(page_num) {
	DocStart = page_num * DocListLen
	reload_page_list()
	await load_documents()
}


export async function reload_page_list() {
	const filter = {
		tag_expr: $.val('tag-query') || null,
		title: $.val('filter-title') || null,
	}

	const res = await query.documents.count(filter)
	if (res.__typename !== 'DocumentCount') {
		return
	}
	const count = res.count

	const page_ct = Math.ceil(count / DocListLen)
	const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
	let this_page = Math.floor(DocStart / DocListLen)
	if (page_ct === 0) {
		this_page = DocStart = 0
	}
	else if (this_page >= page_ct) {
		this_page = page_ct - 1
		DocStart = this_page * DocListLen
	}

	await _('page-list', {
		pages: pages,
		count: page_ct,
		current: this_page,
		total: count,
		no_results_msg: 'No documents found matching the search criteria.',
	}, true)
}


export async function import_documents() {
	const doc_types = ['.txt', '.md', '.doc', '.docx', '.rtf', '.odf', '.odt']
	const files = await api.file_prompt(doc_types.join(','), true).catch(() => null)

	if (files === null) {
		return
	}

	const failed_files = []

	for (const file of files) {
		let title = file.name
		let valid_type = false
		for (const i of doc_types) {
			if (title.endsWith(i)) {
				title = title.substring(0, title.length - i.length)
				valid_type = true
				break
			}
		}
		if (!valid_type) {
			failed_files.push(file.name)
			continue
		}

		const blob_id = (await api.upload(file, () => { }, false, ['__docs'], true, true, 5, true))[0].id

		const res = await mutate.documents.link_blob(title, blob_id)
		if (res.__typename !== 'Document') {
			_.modal.error(res.message)
		}
	}

	if (failed_files.length) {
		_.modal.error(`
			Failed to upload ${failed_files.length === 1 ? 'a document' : 'documents'} due to unsupported document type. Valid types are:<br>
			${doc_types.map(i => `<span class="code">${i}</span>`).join(' ')}
			<br>
			Unsupported document${failed_files.length === 1 ? ' is' : 's are'}:<br>
			<ul>
				${failed_files.map(i => `<li>${i}</li>`).join('')}
			</ul>
		`)
	} else {
		_.modal.checkmark()
	}

	await load_documents()
	reload_page_list()
}


export function help_recover_docs() {
	_.modal({
		type: 'info',
		title: 'How to recover a deleted document',
		text: api.snippit('recover-deleted-document'),
		buttons: ['OK'],
	}).catch(() => { })
}


export function wipe_tag_editor() {
	$('tag-query').value = ''
	navigate_to_page(0)
}


export function set_tag_editor_value(text) {
	const t = text.match(/^\w+$/) ? text : ('"' + text + '"')
	$('tag-query').value = $.val('tag-query') === t ? '' : t
	navigate_to_page(0)
}


export async function set_document_tags(id) {
	const doc_data = await query.documents.get(id)

	_.modal.tags(doc_data.tags, 'countDocumentTagUses').then(async tags => {
		const doc = await mutate.documents.tags(id, tags)
		if (doc.__typename !== 'Document') {
			_.modal.error(doc.message)
			return
		}
		await load_documents()
	})
}


export async function show_tags_how_to() {
	const res = await _.modal({
		type: 'info',
		title: 'What is a tag query?',
		text: await api.get('/html/snippit/tag_query.html'),
		buttons: ['OK', 'More Info'],
	}).catch(() => 'ok')

	if (res === 'ok') return

	dashnav('help/tag_query')
}
