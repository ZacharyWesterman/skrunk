let BookStart = 0
let BookListLen = 15
let InitialLoad = true

await mutate.require('books')
await query.require('books')
await query.require('users')

//Start the NFC reader ONCE per session, and don't stop it.
//Trying to stop/restart it multiple times in a session
//just causes the browser to crash. :/
if (window.NFC === undefined) {
	try {
		window.NFC = new NDEFReader
	} catch (e) {
		window.NFC = {
			scan: () => { }
		}
	}
}

NFC.scan()
export async function init() {
	if (EnabledModules.includes('qr')) _('qrcode-search')

	InitialLoad = true

	window.unload.push(() => {
		NFC.onreading = undefined
	})

	NFC.onreading = async event => {
		$('tagid').value = event.serialNumber

		const res = await query.books.by_rfid(event.serialNumber)

		if (res.__typename !== 'Book') {
			_.modal({
				type: 'error',
				title: 'Book Not Found',
				text: 'No book has been linked with this tag.',
				buttons: ['OK'],
			}).catch(() => { })
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
		options: query.users.list(),
		default: 'Select User',
	})
}

export function manual_input() {
	if ($.val('tagid') !== '') {
		NFC.onreading({ serialNumber: $.val('tagid') })
	}
	else {
		search_books()
	}
}

async function confirm_unlink_book(title, rfid) {
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

	if (res.__typename !== 'BookTag') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => { })
		return true
	}

	search_books()
	return true
}

async function confirm_edit_ebooks(book_data) {
	const modal = await _.modal({
		icon: 'file-pdf',
		title: 'Add E-Books',
		text: `
			Select 1 or more files to add to the list of E-Books.
			<hr>
			<b>${book_data.title}</b>
			${book_data.subtitle ? '<br><i>' + book_data.subtitle + '</i>' : ''}
			<br>
			<span class="suppress">
				By ${book_data.authors.join(', ')}
				<hr>
				<input id="ebook-input" type="file" multiple>
			</span>
		`,
		buttons: ['Submit', 'Delete', 'Cancel'],
	}, () => { }, async choice => { //on validate
		if (choice === 'submit') {
			const files = $('ebook-input').files

			if (!files.length) {
				$.flash('ebook-input')
				return false
			}

			//Upload the file(s)
			let promises = []
			for (let i = 0; i < files.length; ++i) {
				const elem = $('ebook-input').parentElement
				const progress = document.createElement('progress')
				elem.append(document.createElement('br'))
				elem.append(progress)

				progress.value = 0

				promises.push(api.upload(files[i], prog => {
					progress.value = prog.loaded / prog.total * 100
				}, false, ['ebook'], false, true))
			}

			//Once files are done uploading, get the ebook links
			for (const promise of promises) {
				const file = (await promise)[0]
				await mutate.books.append_ebook(book_data.id, file.id)
			}
		}

		return true
	}).catch(() => 'close')

	if (modal !== 'submit') {
		if (modal === 'cancel') { edit_book(book_data.rfid) }
		if (modal === 'delete') {
			unlink_ebooks(book_data)
		}

		return
	}

	_.modal.checkmark()
	search_books()
}

async function unlink_ebooks(book_data) {
	const choice = await _.modal({
		type: 'question',
		title: 'Delete E-Books?',
		text: 'Which ebook do you want to delete?',
		buttons: [...book_data.ebooks.map(b => b.fileType.toUpperCase()), 'Cancel'],
	}).catch(() => 'cancel')

	if (choice === 'cancel') {
		confirm_edit_ebooks(book_data)
		return
	}

	const index = book_data.ebooks.findIndex(b => b.fileType.toLowerCase() === choice)
	const res = await mutate.books.remove_ebook(book_data.id, index)

	if (res.__typename !== 'Book') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	book_data.ebooks = book_data.ebooks.filter(b => b.fileType.toLowerCase() !== choice)
	_.modal.checkmark()
	search_books()
	unlink_ebooks(book_data)
}

export async function edit_book(rfid) {
	let promise_data = query.books.by_rfid(rfid)
	let book_data
	promise_data.then(d => book_data = d)
	let new_data = {}
	let new_owner

	const choice = await _.modal({
		icon: 'pen-to-square',
		title: await api.snippit('delete_button') + (has_perm('admin') ? await api.snippit('ebook_button') : '') + 'Edit Book Info',
		text: '<div name="edit_book">Loading...</div>',
		buttons: ['Update', 'Cancel']
	}, async () => {
		await _('edit_book', promise_data)

		_('dropdown', {
			id: 'book-owner',
			options: query.users.list(),
			default: 'Select User',
		}).then(() => {
			$.wipe('book-owner', book_data.owner.username)
			$.bind('book-owner', () => $.show('button-owner'))
		})

		$('delete').onclick = () => {
			_.modal.return('delete')
		}

		$('ebook').onclick = () => {
			_.modal.return('ebook')
		}
	}, async choice => {
		//validate input
		if (choice !== 'update') return true

		const fields = ['book-owner', 'book-title', 'book-author']
		let valid = true
		for (const i of fields) {
			if (!$.val(i)) {
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

	if (choice === 'delete') {
		if (!(await confirm_unlink_book(book_data.title, book_data.rfid))) edit_book(rfid)
		return
	}
	if (choice === 'ebook') {
		await confirm_edit_ebooks(book_data)
		return
	}

	if (choice !== 'update') return

	//Check if book data has changed
	let data_changed = false
	for (const i in new_data) {
		if (Array.isArray(new_data[i])) {
			if (!new_data[i].every((value, index) => value === book_data[i][index])) data_changed = true
		}
		else {
			if (new_data[i] !== book_data[i]) data_changed = true
		}
	}

	if (!data_changed && new_owner === book_data.owner.username) {
		_.modal({
			text: 'No changes made.',
			no_cancel: true,
		}).catch(() => { })
		setTimeout(_.modal.cancel, 700)
		return
	}

	//Update book data with changes
	if (data_changed) {
		const res = await mutate.books.edit(book_data.id, new_data)

		if (res.__typename !== 'Book') {
			_.modal({
				type: 'error',
				title: 'ERROR',
				text: res.message,
				buttons: ['OK'],
			}).catch(() => { })
			return
		}
	}

	if (new_owner !== book_data.owner.username) {
		//Verify that user wants to transfer ownership
		const confirm = await _.modal({
			type: 'question',
			title: 'Change Book Ownership?',
			text: `You will no longer be able to edit this book's info, and only ${new_owner} will be able to return ownership to you!`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (confirm !== 'yes') {
			edit_book(rfid)
			return
		}

		const res = await mutate.books.set_owner(book_data.id, new_owner)

		if (res.__typename !== 'Book') {
			_.modal({
				type: 'error',
				title: 'ERROR',
				text: res.message,
				buttons: ['OK'],
			}).catch(() => { })
			return
		}
	}

	_.modal.checkmark()
	search_books()
}

export async function navigate_to_page(page_num) {
	//Immediately highlight the new page number
	//(basically, lie to the user and say we're already there, then correct it later)
	for (const i of document.querySelectorAll('.nav-page.border')) {
		i.classList.add('alt')
		i.classList.remove('border')
	}
	for (const i of $('nav-page-' + page_num, true)) {
		i.classList.add('border')
		i.classList.remove('alt')
	}

	//Now actually navigate to the new page
	BookStart = page_num * BookListLen
	await search_books()
}

function valid_fields() {
	$.hide('error-message')
	for (const i of ['author', 'title', 'genre']) {
		try {
			new RegExp($.val(i))
		}
		catch (e) {
			$('error-message').innerText = `Invalid RegEx in "${i}" field: ${e.message}.`
			$.show('error-message', true)
			return false
		}
	}

	return true
}

export async function reset_and_search() {
	BookStart = 0
	await search_books()
}

export async function search_books() {
	$.show('book-header')
	$.show('book-footer')

	if (!valid_fields()) return

	reload_book_count()

	const owner = $.val('owner') || null
	const title = $.val('title') || null
	const author = $.val('author') || null
	const genre = $.val('genre') || null
	const shared = $.checked('shared') //Only filter by shared if field is not indeterminate.

	const filter = {
		owner: owner,
		title: title,
		author: author,
		genre: genre,
		shared: shared,
	}
	const res = await query.books.get(filter, BookStart, BookListLen, { fields: [$.val('sort-by') || 'title'], descending: $.val('sort-order') === 'descending' })

	await _('book', {
		books: res,
		is_admin: SelfUserData.perms.includes('admin'),
	})
}

export async function load_description(id) {
	const field = $('book-desc-' + id)
	if (!field || field.is_loaded) return

	field.is_loaded = true

	const text = await query.books.get_description(id)
	field.innerHTML = (text || '').replace('\n', '<br>')
}

async function reload_book_count() {
	$.on.detach.resize()

	const owner = $.val('owner') || null
	const title = $.val('title') || null
	const author = $.val('author') || null
	const genre = $.val('genre') || null
	const shared = $.checked('shared') //Only filter by shared if field is not indeterminate.

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
	if (page_ct === 0) {
		this_page = BookStart = 0
	}
	else if (this_page >= page_ct) {
		this_page = page_ct - 1
		BookStart = this_page * BookListLen
	}

	const fn = () => _('page-list', {
		pages: pages,
		count: page_ct,
		current: this_page,
		total: count,
		no_results_msg: 'No books found matching the search criteria.',
	}, true)

	fn()
	$.on.resize(fn) //automatically adjust page nav on window resize
}

export async function share_book(is_shared, title, subtitle, author, id, owner) {
	const bookinfo = `<b>${title}</b><br><i>${subtitle}</i><div class="suppress">By ${author}</div>`

	if (owner === api.username) {
		//If user owns the book they're sharing, give options for who to share with.
		let res = await _.modal({
			icon: 'book-open',
			title: 'Share Book',
			text: `${bookinfo}<hr>` + await api.snippit('book_borrow'),
			buttons: is_shared ? ['Share', 'Return', 'Cancel'] : ['Share', 'Cancel'],
		},
			() => { //on load
				_('dropdown', {
					id: 'person',
					options: query.users.list(u => u.username !== api.username),
					default: 'Select User',
				})
			}, choice => { //validate
				if (choice !== 'share') return true

				const who = $('use_other_person').checked ? 'other_person' : 'person'
				if ($.val(who) === '') {
					$.flash(who)
					return false
				}

				return true
			}, choice => { //transform result to something different than buttons
				if (choice === 'return') {
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

						if (res.__typename !== 'Book') {
							_.modal({
								type: 'error',
								title: 'Return Failed',
								text: res.message,
								buttons: ['OK']
							}).catch(() => { })
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

		if (res.is_user) {
			res = await mutate.books.share(id, res.name)
		}
		else {
			res = await mutate.books.share_nonuser(id, res.name)
		}

		if (res.__typename !== 'Book') {
			_.modal({
				type: 'error',
				title: 'Cannot Share Book',
				text: res.message,
				buttons: ['OK'],
			}).catch(() => { })
			return
		}
	}
	else if (is_shared === api.username) {
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

		if (res.__typename !== 'Book') {
			_.modal({
				type: 'error',
				title: 'Return Failed',
				text: res.message,
				buttons: ['OK']
			}).catch(() => { })
			return
		}
	}
	else if (is_shared) {
		//If user doesn't own this book, and it's already borrowed,
		//Give the option to REQUEST to borrow it.
		request_book(is_shared, bookinfo, id, owner)
		return
	}
	else {
		//If user doesn't own this book, they're borrowing it.
		let res = await _.modal({
			icon: 'book-open',
			title: 'Borrow Book',
			text: `Are you currently borrowing this book?<br>If you want to <i>request</i> to borrow it, click "Request".<hr>${bookinfo}`,
			buttons: ['Yes', 'No', 'Request'],
		}).catch(() => 'no')

		if (res === 'request') {
			request_book(is_shared, bookinfo, id, owner)
			return
		}

		if (res !== 'yes') return

		//Mark the book as borrowed by this user.
		res = await mutate.books.borrow(id)

		if (res.__typename !== 'Book') {
			_.modal.error(res.message)
			return
		}
	}

	manual_input()
}

async function request_book(is_shared, bookinfo, id, owner) {
	let res = await _.modal({
		icon: 'book-open',
		title: 'Request to Borrow Book?',
		text: (is_shared ? `This book is already being borrowed by ${is_shared}.` : `This book is not currently being borrowed.`) + `<br>Would you like to request to borrow it?<hr>${bookinfo}`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (res !== 'yes') return

	//Mark the book as borrowed by this user.
	res = await mutate.books.request_borrow(id)

	if (res.__typename !== 'Notification') {
		_.modal.error(res.message)
		return
	}

	_.modal({
		title: 'Notification Sent!',
		text: `A notification has been sent to ${owner} indicating that you'd like to borrow this book.`,
		buttons: ['OK'],
	}).catch(() => { })
}

export async function search_by_qrcode() {
	const qrcode = await qr.load_and_process()
	if (qrcode !== null) {
		$('tagid').value = $.enforce.hex(qrcode)
		manual_input()
	}
}

export async function prompt_ebooks(book_rfid) {
	const book_data = await query.books.by_rfid(book_rfid)
	if (book_data.__typename !== 'Book') {
		_.modal({
			type: 'error',
			title: 'Error',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	let buttons = book_data.ebooks.map(b => b.fileType.toUpperCase())
	let btn_map = {}
	for (const b of book_data.ebooks) {
		//If the url has no slashes, it's an internal file ID.
		const url = (b.url.indexOf('/') === -1) ? `download/${b.url}` : b.url
		btn_map[b.fileType.toLowerCase()] = url
	}

	buttons.push('Cancel')

	const res = await _.modal({
		icon: 'file-pdf',
		title: 'Download E-Book',
		text: 'Please select the file format you would like to download, or hit cancel.',
		buttons: buttons,
	})

	if (res === 'cancel') return

	//Download the selected e-book
	let link = document.createElement('a')
	link.download = book_data.title + '.' + res
	link.href = btn_map[res]
	link.target = '_blank'
	link.click()
}
