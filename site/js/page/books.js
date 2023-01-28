//Start the NFC reader ONCE per session, and don't stop it.
//Trying to stop/restart it multiple times in a session
//just causes the browser to crash. :/
if (window.NFC === undefined)
{
	try {
		window.NFC = new NDEFReader
	} catch(e) {
		window.NFC = {
			scan: () => {}
		}
	}
}

NFC.scan()

window.unload.push(() => {
	NFC.onreading = undefined
})

export function init()
{
	NFC.onreading = async event =>
	{
		const res = await api(`
		query ($rfid: String!) {
			getBookByTag (rfid: $rfid) {
				__typename
				...on Book {
					title
					subtitle
					authors
					thumbnail
					description
				}
				...on BookTagDoesNotExistError {
					message
				}
				...on ApiFailedError {
					message
				}
			}
		}`, {
			rfid: event.serialNumber,
		})

		show_raw_error_message(JSON.stringify(res))

		if (res.__typename !== 'Book')
		{
			_.modal({
				type: 'error',
				title: 'ERROR',
				text: res.message,
				buttons: ['OK'],
			}).catch(() => {})
			return
		}

		await _('book', res)
	}
}
