var modal = async function(config)
{
	await _('modal', config)
	$('modal-window').style.display = 'block'

	return new Promise((resolve, reject) => {
		modal.awaiting = {
			resolve: resolve,
			reject: reject,
		}

		var field = $('modal-button-first')
		if (field)
		{
			$.on.enter(window, field.onclick)
			$.on.escape(window, modal.cancel)
		}
	})
}

modal.cancel = () =>
{
	$.on.detach.enter(window)
	$.on.detach.escape(window)
	$('modal-window').style.display = 'none';
	modal.awaiting.reject()
}

modal.return = value =>
{
	$.on.detach.enter(window)
	$.on.detach.escape(window)
	if (typeof value === 'string') value = value.toLowerCase()
	$('modal-window').style.display = 'none';
	modal.awaiting.resolve(value)
}

modal.upload = async function()
{
	await _('upload_modal', {})
	$('modal-upload-window').style.display = 'block'

	return new Promise((resolve, reject) => {
		modal.awaiting = {
			resolve: resolve,
			reject: reject,
		}
	})
}

modal.upload.return = () =>
{
	$('modal-upload-window').style.display = 'none'
}

modal.upload.start = async function()
{
	async function do_upload(file, dom_progress)
	{
		await api.upload(file, progress => {
			const percent = progress.loaded / progress.total * 100
			dom_progress.value = percent
		})
		$.hide(dom_progress, true)
	}

	const files = $('modal-file').files

	//make sure all files are <=10GB (max file size limit for uploads)
	var too_big = []
	for (var file of files)
	{
		if (file.size > (5 * 1024 * 1024 * 1024))
			too_big.push(`${file.name} (${(file.size / (1024 * 1024 * 1024)).toFixed(2)} GB)`)
	}

	if (too_big.length > 0)
	{
		const amt = too_big.length === 1 ? 'file exceeds' : 'files exceed'
		const amt2 = too_big.length === 1 ? 'that file' : 'those files'

		_.modal({
			title: '<span class="error">Ow, right in the bandwidth!</span>',
			text: `<p>For the sake of performance, there's a <b>5GB</b> limit on file uploads.<br>The following ${amt} this limit:</p><i>${too_big.join('<br>')}</i><p>If you really need to upload ${amt2}, I suggest using an FTP client.`,
			buttons: ['OK'],
		})
		return
	}

	//Add a progress bar for each file to be uploaded.
	var innerHTML = ''
	for (var i = 0; i < files.length; ++i)
	{
		innerHTML += `<progress id="upload-progressbar-${i}" value="0" max="100"></progress>`
	}
	$('upload-progress').innerHTML = innerHTML
	$.show('upload-progress')

	var promises = []
	for (var i = 0; i < files.length; ++i)
	{
		var dom_progress = $('upload-progressbar-'+i)
		promises.push(do_upload(files[i], dom_progress))
	}

	for (var p of promises)
	{
		await p
	}

	await modal({
		title: 'Success',
		text: 'Upload complete',
		buttons: ['OK']
	}).catch(() => {})

	modal.upload.return()
}

export default modal
