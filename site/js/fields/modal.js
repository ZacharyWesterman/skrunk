window.modal = async function(config, onload = () => {}, validate = choice => true, transform = choice => choice)
{
	await _('modal', config)
	onload()
	$('modal-window').close()
	$('modal-window').showModal()
	$('modal-window-expand').classList.add('expanded')

	return new Promise((resolve, reject) => {
		modal.awaiting = {
			resolve: resolve,
			reject: reject,
			validate : validate,
			transform: transform,
		}

		modal.is_open = true
	})
}

modal.is_open = false

modal.cancel = () =>
{
	$('modal-window-expand').classList.remove('expanded')
	setTimeout(() => {$('modal-window').close()}, 200)
	modal.awaiting.reject()
	modal.is_open = false
}

modal.return = value =>
{
	if (typeof value === 'string') value = value.toLowerCase()

	const retn = () => {
		$('modal-window-expand').classList.remove('expanded')
		setTimeout(() => {
			$('modal-window').close()
			modal.awaiting.resolve(modal.awaiting.transform(value))
			modal.is_open = false
		}, 200)
	}

	//Don't close the modal if any fields in it were invalid.
	if (modal.awaiting.validate?.constructor?.name === 'AsyncFunction' || typeof modal.awaiting.validate.then === 'function')
	{
		modal.awaiting.validate(value).then(res => {
			if (res) retn()
		})
	}
	else
	{
		if (modal.awaiting.validate(value)) retn()
	}
}

modal.upload = async function()
{
	await _('upload_modal', {})
	$('modal-upload-window').close()
	$('modal-upload-window').showModal()
	$('modal-upload-expand').classList.add('expanded')

	//Once modal has loaded, inject list of tags.
	let tagList = $('modal-tag-list')
	tagList.innerHTML = ''
	modal.upload.tag_list = []

	function tagHTML(tag)
	{
		return `<div class="tag clickable">${tag}\&nbsp;<b>\&times;</b></div>`
	}

	function tagClicks(tagList)
	{
		const kids = tagList.children
		for (let i = 0; i < kids.length; ++i)
		{
			const child = kids[i]
			const ix = i
			child.onclick = () => {
				modal.upload.tag_list.splice(ix, 1)
				tagList.removeChild(child)
				tagClicks(tagList)
			}
		}
		if (kids.length === 0) tagList.innerHTML = '<i class="disabled">Automatic tags only</i>'
	}
	tagClicks(tagList)

	//when submitting a tag
	const tagSubmit = field => {
		const tag = field.value.trim()
		if (tag.length === 0) return

		if (!modal.upload.tag_list.includes(tag))
		{
			if (modal.upload.tag_list.length === 0) tagList.innerHTML = ''
			modal.upload.tag_list.push(tag)
			tagList.innerHTML += tagHTML(tag)
		}

		field.value = ''
		tagClicks(tagList)
	}

	$('modal-tag-input').nextElementSibling.onclick = () => tagSubmit($('modal-tag-input'))
	$.on.enter($('modal-tag-input'), tagSubmit)

	return new Promise((resolve, reject) => {
		modal.upload.awaiting = {
			resolve: resolve,
			reject: reject,
		}
	})
}

modal.upload.return = () =>
{
	$('modal-upload-expand').classList.remove('expanded')
	setTimeout(() => {$('modal-upload-window').close()}, 200)

	if (api.upload.cancel())
	{
		modal({
			type: 'error',
			title: 'Upload Canceled',
			text: 'All pending file uploads have been stopped.',
			buttons: ['OK'],
		}).catch(() => {})

		modal.upload.awaiting.reject(modal.upload.blobs)
	}
	else
	{
		modal.upload.awaiting.resolve(modal.upload.blobs)
	}
	return modal.upload.blobs
}

modal.upload.start = async function()
{
	const auto_unzip = $('modal-unpack-check').checked
	modal.upload.promises = []
	const tag_list = modal.upload.tag_list
	modal.upload.blobs = []

	async function do_upload(file, dom_progress)
	{
		const blobs = await api.upload(file, progress => {
			const percent = progress.loaded / progress.total * 100
			dom_progress.value = percent
		}, auto_unzip, tag_list)
		$.hide(dom_progress, true)

		modal.upload.blobs.push(...blobs)
	}

	function file_size(size)
	{
		const sizes = ['B', 'KB', 'MB', 'GB', 'EB']
		let this_size = 0
		while (size > 1000)
		{
			size /= 1000
			this_size += 1
		}

		return `${size.toFixed(2)} ${sizes[this_size]}`
	}

	const files = $('modal-file').files

	//make sure all files are <=10GB (max file size limit for uploads)
	let too_big = []
	for (let file of files)
	{
		if (file.size > (5 * 1000 * 1000 * 1000))
			too_big.push(`${file.name} (${file_size(file.size)})`)
	}

	if (too_big.length > 0)
	{
		const amt = too_big.length === 1 ? 'file exceeds' : 'files exceed'
		const amt2 = too_big.length === 1 ? 'that file' : 'those files'

		await _.modal({
			type: 'error',
			title: 'Ow, right in the bandwidth!',
			text: `<p>For the sake of performance, there's a <b>5GB</b> limit on file uploads.<br>The following ${amt} this limit:</p><i>${too_big.join('<br>')}</i><p>If you really need to upload ${amt2}, I suggest using an FTP client.`,
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	//Show a warning if files are >=50MB (may take a long time)
	let large_files = []
	for (let file of files)
	{
		if (file.size >= (50 * 1000 * 1000))
			large_files.push(`${file.name} (${file_size(file.size)})`)
	}

	if (large_files.length > 0)
	{
		const header = large_files.length === 1 ? 'a very large file' : 'some very large files'
		const msg = large_files.length === 1 ? 'A file' : 'Some of the files'
		const it_them = large_files.length === 1 ? 'it' : 'them'
		const res = await _.modal({
			title: `<span class="error">WARNING:</span> You're about to upload ${header}!`,
			text: `<p>${msg} you've selected may take a very long time to upload:</p><i>${large_files.join('<br>')}</i><p>This is still under the hard limit of <b>5GB</b> per file, so you <i>can still upload ${it_them}</i>, but if you have a slow or spotty connection you may want to consider uploading a different way.<br><br><b>Do you want to go ahead and upload?</b></p>`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (res !== 'yes') return
	}

	//Add a progress bar for each file to be uploaded.
	let innerHTML = ''
	for (let i = 0; i < files.length; ++i)
	{
		innerHTML += `<progress id="upload-progressbar-${i}" value="0" max="100"></progress>`
	}
	$('upload-progress').innerHTML = innerHTML
	$.show('upload-progress')

	let promises = []
	for (let i = 0; i < files.length; ++i)
	{
		let dom_progress = $('upload-progressbar-'+i)
		promises.push(do_upload(files[i], dom_progress))
	}
	modal.upload.promises = promises

	for (const p of promises)
	{
		await p
	}

	await modal({
		title: 'Success',
		text: 'Upload complete',
		buttons: ['OK']
	}).catch(() => {})

	modal.upload.promises = []
	modal.upload.return()
}

modal.upload.activate = () =>
{
	$('modal-button').disabled = false
	function zip_exists()
	{
		const files = $('modal-file').files
		for (let i=0; i<files.length; ++i)
		{
			if (files[i].name.endsWith('.zip')) return true
		}
		return false
	}
	$.toggle('modal-auto-unpack', zip_exists())
}

modal.checkmark = () =>
{
	setTimeout(() => {
		$('action-checkmark').classList.remove('checkmark')
	}, 1000)
	$('action-checkmark').classList.add('checkmark')
}

export default modal
