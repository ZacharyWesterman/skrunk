export default {
	delete: async rfid => {
		return await api(`
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
	},

	set_owner: async (id, username) => {
		return await api(`
		mutation ($id: String!, $username: String!) {
			setBookOwner (id: $id, username: $username) {
				__typename
				...on BookTagDoesNotExistError {
					message
				}
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			id: id,
			username: username,
		})
	},

	share: async (id, username) => {
		return await api(`mutation ($id: String!, $username: String!) {
			shareBook (id: $id, username: $username) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
			username: username,
		})
	},

	share_nonuser: async (id, name) => {
		return await api(`mutation ($id: String!, $name: String!) {
			shareBookNonUser (id: $id, name: $name) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
			name: name,
		})
	},

	return: async id => {
		return await api(`mutation ($id: String!) {
			returnBook (id: $id) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
		})
	},

	borrow: async id => {
		return await api(`mutation ($id: String!) {
			borrowBook (id: $id) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
		})
	},

	request_borrow: async id => {
		return await api(`mutation ($id: String!) {
			requestToBorrowBook (id: $id) {
				__typename
				...on MissingConfig { message }
				...on UserDoesNotExistError { message }
				...on WebPushException { message }
				...on InvalidSubscriptionToken { message }
				...on BadNotification { message }
			}
		}`, {
			id: id,
		})
	},

	edit: async (id, changes) => {
		return await api(`mutation ($id: String!, $changes: BookEditData!) {
			editBook (id: $id, changes: $changes) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on UserDoesNotExistError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
			changes: changes,
		})
	},

	create: async book_data => {
		const owner = book_data.owner
		delete book_data.owner

		return await api(`mutation ($owner: String!, $data: BookCreateData!) {
			createBook (owner: $owner, data: $data) {
				__typename
				...on BookTagExistsError { message }
				...on InsufficientPerms { message }
				...on UserDoesNotExistError { message }
			}
		}`, {
			data: book_data,
			owner: owner,
		})
	},

	append_ebook: async (id, ebook_url) => {
		return await api(`mutation ($id: String!, $url: String!) {
			appendEBook(id: $id, url: $url) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on UserDoesNotExistError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
			url: ebook_url,
		})
	},

	remove_ebook: async (id, index) => {
		return await api(`mutation ($id: String!, $index: Int!) {
			removeEBook(id: $id, index: $index) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on UserDoesNotExistError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
			index: index,
		})
	},

	relink_tag: async (id, rfid) => {
		return await api(`mutation ($id: String!, $rfid: String!) {
			relinkBookTag(id: $id, rfid: $rfid) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on UserDoesNotExistError { message }
				...on BookTagExistsError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: id,
			rfid: rfid,
		})
	},
}
