var BookStart = 0
var BookListLen = 15
var InitialLoad = true

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

export async function init()
{
	InitialLoad = true

	window.unload.push(() => {
		NFC.onreading = undefined
	})

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
					owner
					id
					rfid
					categories
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
				title: 'Book Not Found',
				text: 'No book has been linked with this tag.',
				buttons: ['OK'],
			}).catch(() => {})
			return
		}

		_.modal.checkmark()

		$.hide('book-header')
		$.hide('book-footer')

		await _('book', {
			books: [res],
			is_admin: SelfUserData.perms.includes('admin'),
		})
	}


	search_books()

	_('owner', {
		id: 'owner',
		users: query.users.list(),
	})
}

export function manual_input()
{
	if ($.val('tagid') !== '')
	{
		NFC.onreading({serialNumber: $.val('tagid')})
	}
	else
	{
		search_books()
	}
}

export async function confirm_unlink_book(title, rfid)
{
	const choice = await _.modal({
		type: 'question',
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
		rfid: rfid,
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

	search_books()
}

export async function navigate_to_page(page_num)
{
	BookStart = page_num * BookListLen
	await search_books()
}

function valid_fields()
{
	$.hide('error-message')
	for (const i of ['author', 'title', 'genre'])
	{
		try
		{
			new RegExp($.val(i))
		}
		catch(e)
		{
			$('error-message').innerText = `Invalid RegEx in "${i}" field: ${e.message}.`
			$.show('error-message', true)
			return false
		}
	}

	return true
}

export async function search_books()
{
	if (!valid_fields()) return

	const p = reload_book_count()
	if (!InitialLoad) await p
	InitialLoad = false

	const owner = $.val('owner') || null
	const title = $.val('title') || null
	const author = $.val('author') || null
	const genre = $.val('genre') || null

	const res = await api(`
	query ($owner: String, $title: String, $author: String, $genre: String, $start: Int!, $count: Int!) {
		getBooks(owner: $owner, title: $title, author: $author, genre: $genre, start: $start, count: $count) {
			title
			subtitle
			authors
			description
			thumbnail
			owner
			id
			rfid
			categories
		}
	}`, {
		owner: owner,
		title: title,
		author: author,
		genre: genre,
		start: BookStart,
		count: BookListLen,
	})

	await _('book', {
		books: res,
		is_admin: SelfUserData.perms.includes('admin'),
	})
}

async function reload_book_count()
{
	const owner = $.val('owner') || null
	const title = $.val('title') || null
	const author = $.val('author') || null
	const genre = $.val('genre') || null

	const count = await api(`
	query ($owner: String, $title: String, $author: String, $genre: String) {
		countBooks(owner: $owner, title: $title, author: $author, genre: $genre)
	}`, {
		owner: owner,
		title: title,
		author: author,
		genre: genre,
	})

	const page_ct = Math.ceil(count / BookListLen)
	const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
	var this_page = Math.floor(BookStart / BookListLen)
	if (page_ct === 0)
	{
		this_page = BookStart = 0
	}
	else if (this_page >= page_ct)
	{
		this_page = page_ct - 1
		BookStart = this_page * BookListLen
	}

	_('page_list', {
		pages: pages,
		count: page_ct,
		current: this_page,
		total: count,
		no_results_msg: 'No books found matching the search criteria.',
	}, true)
}

export async function share_book(title, subtitle, author, id, owner)
{
	const bookinfo = `<b>${title}</b><br><i>${subtitle}</i><div class="disabled">By ${author}</div>`

	if (owner === api.username)
	{
		//If user owns the book they're sharing, give options for who to share with.
		const res = await _.modal({
			icon: 'book-open',
			title: 'Share Book',
			text: `${bookinfo}<hr>` + await api.snippit('book_borrow'),
			buttons: ['OK', 'Cancel'],
		},
		() => {
			_('user_dropdown', {
				id: '_',
				users: query.users.list(name => name !== api.username),
				default: 'Select User',
			})
		}).catch(() => 'cancel')

		if (res !== 'ok') return

		//User wants to share this book.
		// if ($('use_other_person'))
	}
	else
	{
		//If user doesn't own this book, they're borrowing it.
		const res = await _.modal({
			icon: 'book-open',
			title: 'Borrow Book',
			text: `Are you borrowing this book?<hr>${bookinfo}`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (res !== 'yes') return

		//User wants to borrow this book.
	}
}