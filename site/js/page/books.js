let BookStart = 0
let BookListLen = 15
let InitialLoad = true

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
					owner {
						username
						display_name
					}
					id
					rfid
					categories
					shared
					shareHistory {
						user_id
						name
						display_name
					}
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
	let choice = await _.modal({
		type: 'question',
		title: 'Delete this book?',
		text: `"${title}" will be removed from the library.<br>This will also remove any borrow history for this book.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	choice = await _.modal({
		type: 'question',
		title: 'Really delete this book?',
		text: 'Are you sure?<br>This action is permanent and cannot be undone!',
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
	$.show('book-header')
	$.show('book-footer')

	if (!valid_fields()) return

	const p = reload_book_count()
	if (!InitialLoad) await p
	InitialLoad = false

	const owner = $.val('owner') || null
	const title = $.val('title') || null
	const author = $.val('author') || null
	const genre = $.val('genre') || null
	const shared = $('shared').checked || null //Only filter by shared if field is checked.

	const res = await api(`
	query ($filter: BookSearchFilter, $start: Int!, $count: Int!) {
		getBooks(filter: $filter, start: $start, count: $count) {
			title
			subtitle
			authors
			description
			thumbnail
			owner {
				username
				display_name
			}
			id
			rfid
			categories
			shared
			shareHistory {
				user_id
				name
				display_name
			}
		}
	}`, {
		filter: {
			owner: owner,
			title: title,
			author: author,
			genre: genre,
			shared: shared,
		},
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
	const shared = $('shared').checked || null

	const count = await api(`
	query ($filter: BookSearchFilter) {
		countBooks(filter: $filter)
	}`, {
		filter: {
			owner: owner,
			title: title,
			author: author,
			genre: genre,
			shared: shared,
		},
	})

	const page_ct = Math.ceil(count / BookListLen)
	const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
	let this_page = Math.floor(BookStart / BookListLen)
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

export async function share_book(is_shared, title, subtitle, author, id, owner)
{
	const bookinfo = `<b>${title}</b><br><i>${subtitle}</i><div class="disabled">By ${author}</div>`

	if (owner === api.username)
	{
		//If user owns the book they're sharing, give options for who to share with.
		let res = await _.modal({
			icon: 'book-open',
			title: 'Share Book',
			text: `${bookinfo}<hr>` + await api.snippit('book_borrow'),
			buttons: ['Share', 'Return', 'Cancel'],
		},
		() => { //on load
			_('user_dropdown', {
				id: 'person',
				users: query.users.list(u => u.username !== api.username),
				default: 'Select User',
			})
		}, choice => { //validate
			if (choice !== 'share') return true

			const who = $('use_other_person').checked ? 'other_person' : 'person'
			if ($.val(who) === '')
			{
				$.invalid(who)
				setTimeout(() => $.valid(who), 350)
				return false
			}

			return true
		}, choice => { //transform result to something different than buttons
			if (choice === 'return')
			{
				//Pop a "return book" modal.
				setTimeout(async () => {
					let res = await _.modal({
						icon: 'book-open',
						title: 'Return Book',
						text: `Has this book been returned?<hr>${bookinfo}`,
						buttons: ['Yes', 'No'],
					}).catch(() => 'no')

					if (res !== 'yes') return

					//Mark the book as no longer borrowed by any user.
					res = await api(`mutation ($id: String!) {
						returnBook(id: $id) {
							__typename
							...on BookTagDoesNotExistError { message }
							...on BookCannotBeShared { message }
						}
					}`, {
						id: id,
					})

					if (res.__typename !== 'Book')
					{
						_.modal({
							type: 'error',
							title: 'Return Failed',
							text: res.message,
							buttons: ['OK']
						}).catch(() => {})
						return
					}

					manual_input()
				}, 50)
			}

			if (choice !== 'share') return null

			const non_user = $('use_other_person').checked
			return {
				is_user: !non_user,
				name: $.val(non_user ? 'other_person' : 'person'),
			}
		}).catch(() => null)

		if (res === null) return //Don't refresh page if share was cancelled.

		if (res.is_user)
		{
			res = await api(`mutation ($id: String!, $username: String!) {
				shareBook (id: $id, username: $username) {
					__typename
					...on BookTagDoesNotExistError { message }
					...on BookCannotBeShared { message }
				}
			}`, {
				id: id,
				username: res.name,
			})
		}
		else
		{
			res = await api(`mutation ($id: String!, $name: String!) {
				shareBookNonUser (id: $id, name: $name) {
					__typename
					...on BookTagDoesNotExistError { message }
					...on BookCannotBeShared { message }
				}
			}`, {
				id: id,
				name: res.name,
			})
		}

		if (res.__typename !== 'Book')
		{
			_.modal({
				type: 'error',
				title: 'Cannot Share Book',
				text: res.message,
				buttons: ['OK'],
			}).catch(() => {})
			return
		}
	}
	else if (is_shared === api.username)
	{
		//User is returning this book.
		let res = await _.modal({
			icon: 'book-open',
			title: 'Return Book',
			text: `Are you returning this book?<hr>${bookinfo}`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (res !== 'yes') return

		//Mark the book as no longer borrowed by this user.
		res = await api(`mutation ($id: String!) {
			returnBook(id: $id) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
			}
		}`, {
			id: id,
		})

		if (res.__typename !== 'Book')
		{
			_.modal({
				type: 'error',
				title: 'Return Failed',
				text: res.message,
				buttons: ['OK']
			}).catch(() => {})
			return
		}
	}
	else
	{
		//If user doesn't own this book, they're borrowing it.
		let res = await _.modal({
			icon: 'book-open',
			title: 'Borrow Book',
			text: `Are you borrowing this book?<hr>${bookinfo}`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (res !== 'yes') return

		//Mark the book as borrowed by this user.
		res = await api(`mutation ($id: String!) {
			borrowBook(id: $id) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
			}
		}`, {
			id: id,
		})

		if (res.__typename !== 'Book')
		{
			_.modal({
				type: 'error',
				title: 'Borrow Failed',
				text: res.message,
				buttons: ['OK']
			}).catch(() => {})
			return
		}
	}

	manual_input()
}
