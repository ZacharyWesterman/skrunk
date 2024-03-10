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
let AWAITING_SCAN = false

export function init()
{
	AWAITING_SCAN = false

	window.unload.push(() => {
		NFC.onreading = undefined
	})

	NFC.onreading = event =>
	{
		//Check if a book with the tag ID already exists
		api(`
		query ($rfid: String!) {
			getBookByTag (rfid: $rfid) {
				__typename
			}
		}`, {
			rfid: event.serialNumber,
		}).then(res => {
			if (res.__typename === 'Book')
			{
				_.modal({
					type: 'error',
					title: 'Book Already Linked',
					text: 'A book with this tag has already been cataloged. Please try a different tag or un-link the one from this book.',
					buttons: ['OK'],
				}).catch(() => {})
			}
			else
			{
				$('new-tagid').value = event.serialNumber
				if (AWAITING_SCAN) _.modal.return(event.serialNumber)
				_.modal.checkmark()
			}
		})
	}
}

export async function create_book()
{
	let book_data

	const res = await _.modal({
		icon: 'bookmark',
		title: 'Manually Enter Book',
		text: api.snippit('create_book'),
		buttons: ['OK', 'Cancel'],
	}, () => {}, //on load
	choice => { //validate
		if (choice === 'cancel')
		{
			$('book-thumbnail').wipe()
			return true
		}

		const req_fields = ['book-title', 'book-author', 'book-isbn', 'book-publisher', 'book-published', 'book-pages']
		let valid = true
		for (const i of req_fields)
		{
			if ($.val(i) === '')
			{
				$.flash(i)
				if (valid) $(i).focus()
				valid = false
			}
		}

		const isbn = $.val('book-isbn').replaceAll('-', '')
		if (!isbn.match(/^\d{10}(\d{3})?$/))
		{
			$.flash('book-isbn')
			if (valid) $('book-isbn').focus()
			valid = false
		}

		if (!$.val('book-pages').match(/^\d+$/))
		{
			$.flash('book-pages')
			if (valid) $('book-pages').focus()
			valid = false
		}

		if (!valid) return false

		book_data = {
			title: $.val('book-title').trim(),
			subtitle: $.val('book-subtitle').trim() || null,
			authors: $.val('book-author').split(',').map(x => x.trim()),
			description: $.val('book-description').trim() || null,
			pageCount: parseInt($.val('book-pages').trim()),
			isbn: isbn,
			publisher: $.val('book-publisher').trim(),
			publishedDate: $.val('book-published').trim(),
			thumbnail: $('book-thumbnail').blob_id || null,
		}

		return true
	}).catch(() => {
		$('book-thumbnail').wipe()
		return 'cancel'
	})

	if (res !== 'ok') return

	//Now that book data is entered, wait for rfid to be scanned.
	const p1 = scanning_modal()

	let blob_data = {}
	if (book_data.thumbnail)
	{
		blob_data = await query.blobs.single(book_data.thumbnail)
		book_data.thumbnail = blob_data.id
	}

	const rfid = await p1
	if (rfid === 'cancel') return
	book_data.rfid = rfid

	const result = await mutate.books.create(book_data)

	if (result.__typename !== 'BookTag')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: result.message,
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	_.modal.checkmark()
}

export async function search_books()
{
	const title = $.val('new-title')
	const author = $.val('new-author')

	if (!author && !title)
	{
		await _('booklist', [])
		return
	}

	const res = await api(`
	query ($title: String!, $author: String!) {
		searchBooks(title: $title, author: $author) {
			__typename
			...on BookList {
				books {
					id
					title
					subtitle
					authors
					description
					thumbnail
				}
			}
			...on ApiFailedError {
				message
			}
		}
	}`, {
		title: title,
		author: author,
	})

	if (res.__typename !== 'BookList')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	await _('booklist', res.books)
}

async function scanning_modal()
{
	AWAITING_SCAN = true
	const res = await _.modal({
		icon: 'bookmark',
		title: 'Ready to scan',
		text: api.snippit('rfid_waiting'),
		buttons: EnabledModules.includes('qr') ? ['Use QR', 'Cancel'] : ['Cancel'],
	}, () => {
		const field = $('rfid_manual_input')
		$.bind(field, () => {
			_.modal.return(field.value)
		})

		function keep_focus()
		{
			if (AWAITING_SCAN)
			{
				if (!document.hasFocus() || field !== document.activeElement)
				{
					field.readOnly = true
					field.focus()
					setTimeout(() => {field.readOnly = false}, 50)
				}
				setTimeout(keep_focus, 200)
			}
		}

		keep_focus()
	}).catch(() => 'cancel')

	if (res === 'use qr')
	{
		const qrcode = await qr.load_and_process()
		AWAITING_SCAN = false

		if (qrcode === null) return 'cancel'

		return $.enforce.hex(qrcode)
	}

	AWAITING_SCAN = false
	return res
}

export async function select_book(book_id, book_title)
{
	let tagid = $.val('new-tagid')
	if (tagid === '')
	{
		const res = await scanning_modal()
		if (res === 'cancel') return
		tagid = res
	}

	$('new-tagid').value = '' //Always wipe the RFID field

	const choice = await _.modal({
		title: book_title,
		text: `Do you want to associate this book with Tag ID ${tagid}?`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')
	if (choice !== 'yes') return

	const res = await api(`
	mutation ($rfid: String!, $bookId: String!) {
		linkBookTag (rfid: $rfid, bookId: $bookId) {
			__typename
			...on BookTagExistsError {
				message
			}
			...on ApiFailedError {
				message
			}
		}
	}`, {
		rfid: tagid,
		bookId: book_id,
	})

	if (res.__typename !== 'BookTag')
	{
		_.modal({
			type: 'error',
			title: 'Failed to link book',
			text: res.message,
			buttons: ['OK']
		}).catch(() => {})
		return
	}

	_.modal.checkmark()

	//Wipe all fields
	$('new-tagid').value = ''
	$('new-title').value = ''
	$('new-author').value = ''
	await search_books()
}

export function help()
{
	_.modal({
		type: 'info',
		title: 'Where does this data come from?',
		text: api.snippit('new_book_help'),
		buttons: ['OK'],
	}).catch(() => {})
}
