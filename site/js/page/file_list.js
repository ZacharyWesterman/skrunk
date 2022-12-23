var BlobStart = 0
var BlobListLen = 4

const Editor = new Yace("#tag-query", {
	value: "",
	lineNumbers: false,
	highlighter: window.tag_highlight,
})
Editor.textarea.spellcheck = false

//Convert blob data to be pretty for display purposes.
function conv_blob(blob)
{
	blob.created = date.output(blob.created) //convert dates to local time

	var sizes = ['GB', 'MB', 'KB']
	var sizetype = 'B'
	while (blob.size >= 1000)
	{
		sizetype = sizes.pop()
		blob.size /= 1000
	}
	blob.size = blob.size.toFixed(2) + ' ' + sizetype //convert size to human-readable format
	return blob
}

async function get_blobs(start, count)
{
	var blobs = await api(`query ($username: String, $start: Int!, $count: Int!, $tags: String){
		getBlobs(username: $username, start: $start, count: $count, tags: $tags) {
			__typename
			...on BlobList {
				blobs {
					id
					ext
					mimetype
					name
					size
					creator
					created
					tags
				}
			}
			...on BadTagQuery {
				message
			}
		}
	}`, {
		username: null,
		start: start,
		count: count,
		tags: Editor.value,
	})

	if (blobs.blobs)
	{
		blobs.blobs = blobs.blobs.map(conv_blob)
	}

	return blobs
}

async function get_blob(blob_id)
{
	var blob = await api(`query ($id: String!){
		getBlob (id: $id) {
			id
			ext
			mimetype
			name
			size
			creator
			created
			tags
		}
	}`, {
		id: blob_id,
	})

	if (blob.__typename === 'Blob')
	{
		blob = conv_blob(blob)
	}

	return blob
}

window.navigate_to_page = async function(page_num)
{
	BlobStart = page_num * BlobListLen
	await reload_blobs()
}

window.copy_to_clipboard = async function(id)
{
	await navigator.clipboard.writeText(id)
	_.modal({
		text: 'Copied file path to clipboard!',
	}).catch(() => {})
	setTimeout(_.modal.cancel, 1200)
}

async function reload_page_list()
{
	var count = await api(`query ($username: String, $tags: String){
		countBlobs(username: $username, tags: $tags) {
			__typename
			...on BlobCount {
				count
			}
			...on BadTagQuery {
				message
			}
		}
	}`, {
		username: null,
		tags: Editor.value,
	})
	if (count.__typename !== 'BlobCount')
	{
		$('tag-error').innerText = count.message
		return
	}
	$('tag-error').innerText = ''
	count = count.count

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

window.reload_blobs = async function()
{
	reload_page_list()

	var blobs = await get_blobs(BlobStart, BlobListLen)
	if (blobs.__typename !== 'BlobList')
	{
		$('tag-error').innerText = blobs.message
		return
	}
	$('tag-error').innerText = ''
	blobs = blobs.blobs

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

window.confirm_delete_blob = async function(id, name)
{
	const choice = await _.modal({
		title: 'Permanently delete file?',
		text: `Are you sure you want to delete "<i>${name}</i>"? This action is permanent and cannot be undone.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await api(`mutation ($id: String!) {
		deleteBlob(id: $id) {
			__typename
			...on BlobDoesNotExistError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`, {id: id})

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

window.show_tags_how_to = async () => {
	const res = await _.modal({
		type: 'info',
		title: 'What is a tag query?',
		text: await api.get('/html/snippit/tag_query.html'),
		buttons: ['OK', 'More Info'],
	}).catch(() => 'ok')

	if (res === 'ok') return

	dashnav('/html/help/tag_query.html')
}

window.set_blob_tags = async id => {
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

	const blob = await api(`mutation ($id: String!, $tags: [String!]!) {
		setBlobTags (id: $id, tags: $tags) {
			__typename
			...on BlobDoesNotExistError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`, {
		id: id,
		tags: blob_data.tags,
	})

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

window.unload.push(() => {
	delete window.reload_blobs
	delete window.confirm_delete_blob
	delete window.copy_to_clipboard
	delete window.show_tags_how_to
	delete window.set_blob_tags
	_.modal.upload.return = old_modal_retn
})
