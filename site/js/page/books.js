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

let ThisBook = null

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
			}
		}`, {
			rfid: event.serialNumber,
		})

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

		ThisBook = event.serialNumber
		await _('book', res)
	}
}

export async function confirm_unlink_book(title)
{
	const choice = await _.modal({
		title: 'Unlink this book?',
		text: `"${title}" will no longer be associated with this RFID tag.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await api(`
	mutation ($rfid: String!) {
		unlinkBookTag (rfid: $rfid) {
			__typename
			...on BookTagDoesNotExistError {
				message
			}
			...on InsufficientPerms {
				message
			}
		}
	}`, {
		rfid: ThisBook,
	})

	if (res.__typename !== 'BookTag')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	$('book').innerText = `Unlinked tag for "${title}"`
}
