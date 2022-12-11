async function get_blobs()
{
	return await api(`query ($start: Int!, $count: Int!){
		getAllBlobs(start: $start, count: $count) {
			id
			ext
			mimetype
			name
			creator
			created
		}
	}`, {
		start: 0,
		count: 20,
	})
}

window.reload_blobs = async function()
{
	var blobs = await get_blobs()
	for (var i in blobs)
	{
		blobs[i].created = date.output(blobs[i].created) //convert dates to local time
	}
	await _('blob_list', blobs)
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

	reload_blobs()
}

reload_blobs()

var old_modal_retn = _.modal.upload.return
_.modal.upload.return = () => {
	old_modal_retn()
	reload_blobs()
}

window.unload.push(() => {
	delete window.reload_blobs
	delete window.confirm_delete_blob
	_.modal.upload.return = old_modal_retn
})
