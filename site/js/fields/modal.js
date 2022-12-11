var modal = async function(config)
{
	await _('modal', config)
	$('modal-window').style.display = 'block'

	return new Promise((resolve, reject) => {
		modal.awaiting = {
			resolve: resolve,
			reject: reject,
		}
	})
}

modal.cancel = () =>
{
	modal.awaiting.reject()
	$('modal-window').style.display = 'none';
}

modal.return = value =>
{
	if (typeof value === 'string') value = value.toLowerCase()
	modal.awaiting.resolve(value)
	$('modal-window').style.display = 'none';
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
