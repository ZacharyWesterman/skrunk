var modal = async function(config)
{
	await _('modal', config)
	$('modal-window').style.display = 'block';

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
	modal.awaiting.resolve(value.toLowerCase())
	$('modal-window').style.display = 'none';
}

export default modal
