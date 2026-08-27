let BlobStart = 0
let BlobListLen = 15

await mutate.require('blobs')
await query.require('blobs')
await query.require('users')

//run this everytime page is imported
export async function init() {
	await _('dropdown', {
		id: 'blob-filter-creator',
		options: query.users.list(),
		default: 'Anyone',
	})
	$('blob-filter-creator').onchange = reset_and_search

	//Load query from urlparams (if it's there)
	let q = {}
	try { q = JSON.parse(environment.get_param('query')) } catch { }
	for (const i in q) {
		if (i === 'tag') {
			$('tag-query').value = q[i]
		} else {
			const f = $('blob-filter-' + i)
			if (f.type === 'checkbox') {
				if (q[i] === null) {
					f.indeterminate = true
				} else {
					f.checked = q[i]
				}
			}
			else {
				f.value = q[i]
			}
			$.toggle_expand('extra-search-fields', true)
			$('toggle-chevron').classList.add('inverted')
		}
	}

	$.bind('blob-filter-title', reset_and_search)

	const old_modal_retn = _.modal.upload.return
	_.modal.upload.return = () => {
		old_modal_retn()
		reload_blobs()
	}

	window.unload.push(() => {
		_.modal.upload.return = old_modal_retn
		environment.set_param('query', null)
	})

	reset_and_search()
}

export function wipe_tag_editor() {
	$('tag-query').value = ''
	reset_and_search()
}

export function set_tag_editor_value(text) {
	const t = text.match(/^\w+$/) ? text : ('"' + text + '"')
	$('tag-query').value = $.val('tag-query') === t ? '' : t
	reset_and_search()
}

async function get_blobs(start, count) {
	const title = $.val('blob-filter-title')
	const creator = $.val('blob-filter-creator') === '' ? null : $.val('blob-filter-creator')
	const date_from = date.from_field('blob-filter-from')
	const date_to = date.from_field('blob-filter-to', 1)
	const ephemeral = $.checked('blob-filter-ephemeral')
	const tag_query = $.val('tag-query')

	let q = {}
	let has = false
	for (const i of ['title', 'creator', 'from', 'to', 'ephemeral']) {
		const v = $.val('blob-filter-' + i)
		if (v !== '' && v !== false) {
			q[i] = v
			has = true
		}
	}
	if (tag_query) {
		q.tag = tag_query
		has = true
	}
	environment.set_param('query', has && JSON.stringify(q))

	return await query.blobs.list(
		creator,
		start,
		count,
		tag_query,
		date_from,
		date_to,
		title,
		ephemeral,
		{
			fields: [$.val('sort-by') || 'created'],
			descending: $.val('sort-order') === 'descending',
		}
	)
}

async function get_blob(blob_id) {
	return await query.blobs.get(blob_id)
}

export async function navigate_to_page(page_num) {
	BlobStart = page_num * BlobListLen
	await reload_blobs()
}

export async function copy_to_clipboard(id) {
	await navigator.clipboard.writeText(`${id}`)
	_.modal({
		text: 'Copied URL to clipboard!',
		no_cancel: true,
	}).catch(() => { })
	setTimeout(_.modal.cancel, 1200)
}

async function reload_page_list() {
	const title = $.val('blob-filter-title') || null
	const creator = $.val('blob-filter-creator') || null
	const date_from = date.from_field('blob-filter-from') || null
	const date_to = date.from_field('blob-filter-to', 1) || null
	const ephemeral = $.checked('blob-filter-ephemeral')
	const tag_query = $.val('tag-query')
	const res = await query.blobs.count(creator, tag_query, date_from, date_to, title, ephemeral)
	if (res.__typename !== 'BlobCount') {
		$('tag-error').innerText = res.message
		return
	}
	$('tag-error').innerText = ''
	const count = res.count

	const page_ct = Math.ceil(count / BlobListLen)
	const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
	let this_page = Math.floor(BlobStart / BlobListLen)
	if (page_ct === 0) {
		this_page = BlobStart = 0
	}
	else if (this_page >= page_ct) {
		this_page = page_ct - 1
		BlobStart = this_page * BlobListLen
	}

	await _('page-list', {
		pages: pages,
		count: page_ct,
		current: this_page,
		total: count,
		no_results_msg: 'No files found matching the search criteria.',
	}, true)
}

export async function reset_and_search() {
	BlobStart = 0
	await reload_blobs()
}

export async function reload_blobs() {
	reload_page_list()

	const res = await get_blobs(BlobStart, BlobListLen)
	if (res.__typename !== 'BlobList') {
		$('tag-error').innerText = res.message
		return
	}
	$('tag-error').innerText = ''
	const blobs = res.blobs

	let innerHTML = ''
	for (const i in blobs) {
		innerHTML += `<div id="blob-card-${blobs[i].id}" template="blob"></div>\n`
	}
	$('blob-list').innerHTML = innerHTML

	for (const i in blobs) {
		await _(`blob-card-${blobs[i].id}`, blobs[i])
	}
}

export async function confirm_delete_blob(id, name) {
	const choice = await _.modal({
		type: 'question',
		title: 'Permanently delete file?',
		text: `Are you sure you want to delete "<i>${name}</i>"? This action is permanent and cannot be undone.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await mutate.blobs.delete(id)
	if (res.__typename !== 'Blob') {
		_.modal.error(res.message)
		return
	}

	reload_page_list()
	$.hide(`blob-card-${id}`, true)
	setTimeout(() => remove_blob(id), 300)
}

async function remove_blob(id) {
	let card = $(`blob-card-${id}`)
	card.parentElement.removeChild(card)

	const ct = $('blob-list').childElementCount
	let innerHTML = ''

	let blobs = await get_blobs(BlobStart + ct, BlobListLen - ct)
	if (blobs.__typename !== 'BlobList') {
		$('tag-error').innerText = blobs.message
		return
	}
	$('tag-error').innerText = ''
	blobs = blobs.blobs

	for (const i in blobs) {
		innerHTML += `<div id="blob-card-${blobs[i].id}" template="blob"></div>\n`
	}
	$('blob-list').innerHTML += innerHTML
	set_field_logic($('blob-list'))

	for (const i in blobs) {
		await _(`blob-card-${blobs[i].id}`, blobs[i])
	}
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

export async function show_ephemeral_info() {
	await _.modal({
		type: 'info',
		title: 'What is an <span class="emphasis">ephemeral</span> file?',
		text: await api.snippit('ephemeral_files'),
		buttons: ['OK'],
	}).catch(() => 'ok')
}

export async function set_blob_tags(id) {
	const blob_data = await get_blob(id)

	_.modal.tags(blob_data.tags, 'countBlobTagUses').then(async tags => {
		const blob = await mutate.blobs.tags(id, tags)
		if (blob.__typename !== 'Blob') {
			_.modal.error(blob.message)
			return
		}
		await reload_blobs()
	}).catch(() => { })
}

export async function download_all() {
	const title = $.val('blob-filter-title') || null
	const creator = $.val('blob-filter-creator') || null
	const date_from = date.from_field('blob-filter-from') || null
	const date_to = date.from_field('blob-filter-to') || null
	const ephemeral = $.checked('blob-filter-ephemeral')
	const tag_query = $.val('tag-query')

	await _.modal.download_zip(
		() => query.blobs.size(creator, tag_query, date_from, date_to, title, ephemeral),
		(uid) => mutate.blobs.create_zip(creator, tag_query, date_from, date_to, title, ephemeral, uid)
	)
}

export async function toggle_blob_hidden(blob_id) {
	const field = $(`hide-button-${blob_id}`)
	const icon = field.children[0]
	const tooltip = field.children[1]

	const hidden = icon.classList.contains('fa-eye-slash')

	const res = await mutate.blobs.set_hidden(blob_id, !hidden)
	if (res.__typename !== 'Blob') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	_.modal.checkmark()

	const old_icon = res.hidden ? 'fa-eye' : 'fa-eye-slash'
	const new_icon = res.hidden ? 'fa-eye-slash' : 'fa-eye'

	tooltip.innerText = res.hidden ? 'File is only visible to you' : 'File is visible to everyone'

	icon.classList.remove(old_icon)
	icon.classList.add(new_icon)

	const title = $(`title-${blob_id}`)

	//Make icon pop a bit if hidden
	if (res.hidden) {
		icon.classList.add('emphasis')
		title.classList.add('emphasis')
	} else {
		icon.classList.remove('emphasis')
		title.classList.remove('emphasis')
	}
}

export function view_pdf(url) {
	//On desktop, open view in-browser.
	const elem = $('pdf-viewer')
	elem.innerHTML = `<iframe frameborder="0" style="width: 100%; height: 100%;" src="${url}"></iframe>
	<div class="clickable close-pdf-viewer">
		<i style="position: relative; top:15%;" class="fa-solid fa-times fa-lg"></i>
	</div>`

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
