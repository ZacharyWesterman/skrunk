let BookStart = 0
let BookListLen = 15
let InitialLoad = true

await mutate.require('books')
await query.require('books')
await query.require('users')

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
	three_state_checkbox()

	window.unload.push(() => {
		NFC.onreading = undefined
	})

	NFC.onreading = async event =>
	{
		$('tagid').value = event.serialNumber

		const res = await query.books.by_rfid(event.serialNumber)

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

export function three_state_checkbox()
{
	const f = $('shared')
	if (f.state === undefined) f.state = 0 //will transition to indeterminate

	f.state = [1, 2, 0][f.state]

	f.checked = f.state === 2
	f.indeterminate = f.state === 1
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

async function confirm_unlink_book(title, rfid)
{
	let choice = await _.modal({
		type: 'question',
		title: 'Delete this book?',
		text: `"${title}" will be removed from the library.<br>This will also remove any borrow history for this book.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return false

	choice = await _.modal({
		type: 'question',
		title: 'Really delete this book?',
		text: 'Are you sure?<br>This action is permanent and cannot be undone!',
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return false

	const res = await mutate.books.delete(rfid)

	if (res.__typename !== 'BookTag')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => {})
		return true
	}

	search_books()
	return true
}

export async function edit_book(rfid)
{
	let promise_data = query.books.by_rfid(rfid)
	let book_data
	promise_data.then(d => book_data = d)
	let new_data = {}
	let new_owner

	const choice = await _.modal({
		title: 'Edit Book Info',
		text: '<div name="edit_book">Loading...</div>',
		buttons: ['Update', 'Cancel']
	}, async () => {
		await _('edit_book', promise_data)

		_('user_dropdown', {
			id: 'book-owner',
			users: query.users.list(),
			default: 'Select User',
		}).then(() => { $('book-owner').value = book_data.owner.username })

		$('delete').onclick = () => {
			_.modal.return('delete')
		}
	}, async choice => {
		//validate input
		if (choice !== 'update') return true

		const fields = ['book-owner', 'book-title', 'book-author']
		let valid = true
		for (const i of fields)
		{
			if (!$.val(i))
			{
				$.flash(i)
				valid = false
			}
		}

		new_owner = $.val('book-owner')
		new_data = {
			title: $.val('book-title'),
			subtitle: $.val('book-subtitle') || null,
			authors: $.val('book-author').split(',').map(x => x.trim()),
		}

		//Don't allow update if none of the data has changed
		return valid
	}).catch(() => 'cancel')

	if (choice === 'delete')
	{
		if ( !(await confirm_unlink_book(book_data.title, book_data.rfid)) ) edit_book(rfid)
		return
	}
	if (choice !== 'update') return

	//Check if book data has changed
	let data_changed = new_owner !== book_data.owner.username
	for (const i in new_data)
	{
		if (Array.isArray(new_data[i]))
		{
			if (!new_data[i].every((value, index) => value === book_data[i][index])) data_changed = true
		}
		else
		{
			if (new_data[i] !== book_data[i]) data_changed = true
		}
	}

	if (!data_changed)
	{
		_.modal({
			title: 'No&nbsp;changes&nbsp;made',
			no_cancel: true,
		}).catch(() => {})
		setTimeout(_.modal.cancel, 700)
		return
	}

	if (new_owner !== book_data.owner.username)
	{
		//Verify that user wants to transfer ownership
		const confirm = await _.modal({
			type: 'question',
			title: 'Change Book Ownership?',
			text: `You will no longer be able to edit this book's info, and only ${new_owner} will be able to return ownership to you!`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (confirm !== 'yes')
		{
			edit_book(rfid)
			return
		}

		const res = await mutate.books.set_owner(book_data.id, new_owner)

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
	}

	_.modal.checkmark()
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
	const shared = $('shared').indeterminate ? null : $('shared').checked //Only filter by shared if field is not indeterminate.

	const filter = {
		owner: owner,
		title: title,
		author: author,
		genre: genre,
		shared: shared,
	}
	const res = await query.books.get(filter, BookStart, BookListLen)

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
	const shared = $('shared').indeterminate ? null : $('shared').checked //Only filter by shared if field is not indeterminate.

	const filter = {
		owner: owner,
		title: title,
		author: author,
		genre: genre,
		shared: shared,
	}
	const count = await query.books.count(filter)

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
				$.flash(who)
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
					res = await mutate.books.return(id)

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
			res = await mutate.books.share(id, res.name)
		}
		else
		{
			res = await mutate.books.share_nonuser(id, res.name)
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
		res = await mutate.books.return(id)

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
		res = await mutate.books.borrow(id)

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
