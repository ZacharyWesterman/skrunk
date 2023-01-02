var BlobStart = 0
var BlobListLen = 4

const Editor = new Yace("#tag-query", {
	value: "",
	lineNumbers: false,
	highlighter: tag_highlight,
})
Editor.textarea.spellcheck = false

//run this everytime page is imported
export function init()
{
	reload_blobs()

	var old_modal_retn = _.modal.upload.return
	_.modal.upload.return = () => {
		old_modal_retn()
		reload_blobs()
	}

	$.on.blur(Editor.textarea, () => {
		BlobStart = 0
		reload_blobs()
	})

	window.unload.push(() => {
		_.modal.upload.return = old_modal_retn
	})
}

async function get_blobs(start, count)
{
	return await query.blobs.get(null, start, count, Editor.value)
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
	await navigator.clipboard.writeText(id)
	_.modal({
		text: 'Copied file path to clipboard!',
	}).catch(() => {})
	setTimeout(_.modal.cancel, 1200)
}

async function reload_page_list()
{
	const res = await query.blobs.count(null, Editor.value)
	if (res.__typename !== 'BlobCount')
	{
		$('tag-error').innerText = res.message
		return
	}
	$('tag-error').innerText = ''
	const count = res.count

	const page_ct = Math.ceil(count / BlobListLen)
	const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
	var this_page = Math.floor(BlobStart / BlobListLen)
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

	var innerHTML = ''
	for (var i in blobs)
	{
		innerHTML += `<div id="blob-card-${blobs[i].id}" template="blob"></div>\n`
	}
	$('blob-list').innerHTML = innerHTML

	for (var i in blobs)
	{
		await _(`blob-card-${blobs[i].id}`, blobs[i])
	}
}

export async function confirm_delete_blob(id, name)
{
	const choice = await _.modal({
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
	var card = $(`blob-card-${id}`)
	card.parentElement.removeChild(card)

	const ct = $('blob-list').childElementCount
	var innerHTML = ''

	var blobs = await get_blobs(BlobStart + ct, BlobListLen - ct)
	if (blobs.__typename !== 'BlobList')
	{
		$('tag-error').innerText = blobs.message
		return
	}
	$('tag-error').innerText = ''
	blobs = blobs.blobs

	for (var i in blobs)
	{
		innerHTML += `<div id="blob-card-${blobs[i].id}" template="blob"></div>\n`
	}
	$('blob-list').innerHTML += innerHTML

	for (var i in blobs)
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
		var taglist = $('modal-tag-list')
		var kids = taglist.children
		for (var i = 0; i < kids.length; ++i)
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
		var innerHTML = ''
		for (var tag of blob_data.tags) { innerHTML += tagHTML(tag) }
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
