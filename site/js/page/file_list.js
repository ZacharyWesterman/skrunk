let BlobStart = 0
let BlobListLen = 15

let Editor

//Load Yace only when needed
import Yace from 'https://unpkg.com/yace?module' //For code editing textareas
window.Yace = Yace

//run this everytime page is imported
export async function init()
{
	await _('user_dropdown', {
		id: 'blob-filter-creator',
		users: query.users.list(),
	})
	$('blob-filter-creator').onchange = reload_blobs;

	Editor = new Yace("#tag-query", {
		value: "",
		lineNumbers: false,
		highlighter: tag_highlight,
	})
	Editor.textarea.spellcheck = false

	$.bind(Editor.textarea, () => {
		BlobStart = 0
		reload_blobs()
	}, 500, true)

	$.bind('blob-filter-title', reload_blobs)

	const old_modal_retn = _.modal.upload.return
	_.modal.upload.return = () => {
		old_modal_retn()
		reload_blobs()
	}

	window.unload.push(() => {
		_.modal.upload.return = old_modal_retn
	})
}

async function get_blobs(start, count)
{
	const title = $.val('blob-filter-title');
	const creator = $.val('blob-filter-creator') === '' ? null : $.val('blob-filter-creator')
	const date_from = date.from_field('blob-filter-from')
	const date_to = date.from_field('blob-filter-to')
	return await query.blobs.get(
		creator,
		start,
		count,
		Editor.value,
		date_from,
		date_to,
		title,
	)
}

async function get_blob(blob_id)
{
	return await query.blobs.single(blob_id)
}

export async function navigate_to_page(page_num)
{
	BlobStart = page_num * BlobListLen
	await reload_blobs()
}

export async function copy_to_clipboard(id)
{
	await navigator.clipboard.writeText(`${window.location}/blob/${id}`)
	_.modal({
		text: 'Copied URL to clipboard!',
	}).catch(() => {})
	setTimeout(_.modal.cancel, 1200)
}

async function reload_page_list()
{
	const title = $.val('blob-filter-title');
	const creator = $.val('blob-filter-creator') === '' ? null : $.val('blob-filter-creator')
	const date_from = date.from_field('blob-filter-from')
	const date_to = date.from_field('blob-filter-to')
	const res = await query.blobs.count(creator, Editor.value, date_from, date_to, title)
	if (res.__typename !== 'BlobCount')
	{
		$('tag-error').innerText = res.message
		return
	}
	$('tag-error').innerText = ''
	const count = res.count

	const page_ct = Math.ceil(count / BlobListLen)
	const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
	let this_page = Math.floor(BlobStart / BlobListLen)
	if (page_ct === 0)
	{
		this_page = BlobStart = 0
	}
	else if (this_page >= page_ct)
	{
		this_page = page_ct - 1
		BlobStart = this_page * BlobListLen
	}

	await _('page_list', {
		pages: pages,
		count: page_ct,
		current: this_page,
		total: count,
		no_results_msg: 'No files found matching the search criteria.',
	}, true)
}

export async function reload_blobs()
{
	reload_page_list()

	const res = await get_blobs(BlobStart, BlobListLen)
	if (res.__typename !== 'BlobList')
	{
		$('tag-error').innerText = res.message
		return
	}
	$('tag-error').innerText = ''
	const blobs = res.blobs

	let innerHTML = ''
	for (const i in blobs)
	{
		innerHTML += `<div id="blob-card-${blobs[i].id}" template="blob"></div>\n`
	}
	$('blob-list').innerHTML = innerHTML

	for (const i in blobs)
	{
		await _(`blob-card-${blobs[i].id}`, blobs[i])
	}
}

export async function confirm_delete_blob(id, name)
{
	const choice = await _.modal({
		type: 'question',
		title: 'Permanently delete file?',
		text: `Are you sure you want to delete "<i>${name}</i>"? This action is permanent and cannot be undone.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await mutate.blobs.delete(id)
	if (res.__typename !== 'Blob')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	reload_page_list()
	$.hide(`blob-card-${id}`, true)
	setTimeout(() => remove_blob(id), 300)
}

async function remove_blob(id)
{
	let card = $(`blob-card-${id}`)
	card.parentElement.removeChild(card)

	const ct = $('blob-list').childElementCount
	let innerHTML = ''

	let blobs = await get_blobs(BlobStart + ct, BlobListLen - ct)
	if (blobs.__typename !== 'BlobList')
	{
		$('tag-error').innerText = blobs.message
		return
	}
	$('tag-error').innerText = ''
	blobs = blobs.blobs

	for (const i in blobs)
	{
		innerHTML += `<div id="blob-card-${blobs[i].id}" template="blob"></div>\n`
	}
	$('blob-list').innerHTML += innerHTML
	set_field_logic($('blob-list'))

	for (const i in blobs)
	{
		await _(`blob-card-${blobs[i].id}`, blobs[i])
	}
}

export async function show_tags_how_to()
{
	const res = await _.modal({
		type: 'info',
		title: 'What is a tag query?',
		text: await api.get('/html/snippit/tag_query.html'),
		buttons: ['OK', 'More Info'],
	}).catch(() => 'ok')

	if (res === 'ok') return

	dashnav('/html/help/tag_query.html')
}

export async function set_blob_tags(id)
{
	const blob_data = await get_blob(id)

	function tagHTML(tag)
	{
		return `<div class="tag clickable">${tag}\&nbsp;<b>\&times;</b></div>`
	}

	function tagClicks()
	{
		let taglist = $('modal-tag-list')
		const kids = taglist.children
		for (const i = 0; i < kids.length; ++i)
		{
			const child = kids[i]
			const ix = i
			child.onclick = () => {
				blob_data.tags.splice(ix, 1)
				taglist.removeChild(child)
				tagClicks()
			}
		}
	}

	const res = await _.modal({
		title: 'Update Tags',
		text: await api.get('/html/snippit/blob_tag_modal.html'),
		buttons: ['OK', 'Cancel'],
	}, () => {
		//Once modal has loaded, inject list of tags.
		let innerHTML = ''
		for (const tag of blob_data.tags) { innerHTML += tagHTML(tag) }
		$('modal-tag-list').innerHTML = innerHTML
		tagClicks()

		//when submitting a tag
		const tagSubmit = field => {
			const tag = field.value.trim()
			if (tag.length === 0) return

			if (!blob_data.tags.includes(tag))
			{
				blob_data.tags.push(tag)
				$('modal-tag-list').innerHTML += tagHTML(tag)
			}

			field.value = ''
			tagClicks()
		}

		$('modal-tag-input').nextElementSibling.onclick = () => tagSubmit($('modal-tag-input'))
		$.on.enter($('modal-tag-input'), tagSubmit)
	}, false).catch(() => 'cancel')

	if (res !== 'ok') return

	const blob = await mutate.blobs.tags(id, blob_data.tags)
	if (blob.__typename !== 'Blob')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	await reload_blobs()
}
