var BookStart = 0
var BookListLen = 15

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

export async function init()
{
	NFC.onreading = async event =>
	{
		$('tagid').value = event.serialNumber

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
			$('book').innerText = 'No book with that RFID was found.'
			return
		}

		ThisBook = event.serialNumber
		await _('book', [res])
	}

	await _('owner', {
		id: 'owner',
		users: await query.users.list(),
	})

	$.bind('tagid', manual_input)
	$.bind('title', search_books)
	$.bind('author', search_books)
	await search_books()
}

function manual_input()
{
	if ($.val('tagid') !== '')
	{
		NFC.onreading({serialNumber: $.val('tagid')})
	}
}

export async function confirm_unlink_book(title)
{
	const choice = await _.modal({
		title: 'Unlink this book?',
		text: `"${title}" will be removed from the library.`,
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

	$('book').innerText = `Deleted "${title}"`
}

export async function search_books()
{
	const owner = $.val('owner') || null
	const title = $.val('title') || null
	const author = $.val('author') || null

	const res = await api(`
	query ($owner: String, $title: String, $author: String, $start: Int!, $count: Int!) {
		getBooks(owner: $owner, title: $title, author: $author, start: $start, count: $count) {
			title
			subtitle
			authors
			description
			thumbnail
		}
	}`, {
		owner: owner,
		title: title,
		author: author,
		start: BookStart,
		count: BookListLen,
	})

	console.log(res)
}