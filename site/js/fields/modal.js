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
	var file = $('modal-file').files[0]
	$.show('upload-progress')

	await api.upload(file, progress => {
		const percent = progress.loaded / progress.total * 100
		$('upload-progress').value = percent
	})

	await modal({
		title: 'Success',
		text: 'Upload complete',
		buttons: ['OK']
	}).catch(() => {})

	modal.upload.return()
}

export default modal
