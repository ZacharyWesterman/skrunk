var BlobStart = 0
var BlobListLen = 4

async function get_blobs(start, count)
{
	return await api(`query ($username: String, $start: Int!, $count: Int!, $tags: String){
		getBlobs(username: $username, start: $start, count: $count, tags: $tags) {
			__typename
			...on BlobList {
				blobs {
					id
					ext
					mimetype
					name
					creator
					created
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
		tags: $('tag-query').value,
	})
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
		tags: $('tag-query').value,
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
		blobs[i].created = date.output(blobs[i].created) //convert dates to local time
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
			title: '<span class="error">ERROR</span>',
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
		blobs[i].created = date.output(blobs[i].created) //convert dates to local time
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

$.on.enter($('tag-query'), () => {
	BlobStart = 0
	reload_blobs()
})

window.unload.push(() => {
	delete window.reload_blobs
	delete window.confirm_delete_blob
	delete window.copy_to_clipboard
	_.modal.upload.return = old_modal_retn
})
