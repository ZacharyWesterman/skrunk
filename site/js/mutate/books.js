export default {
	delete: async rfid =>
	{
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

	set_owner: async (id, username) =>
	{
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

	share: async (id, username) =>
	{
		return await api(`mutation ($id: String!, $username: String!) {
			shareBook (id: $id, username: $username) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
			}
		}`, {
			id: id,
			username: username,
		})
	},

	share_nonuser: async (id, name) =>
	{
		return await api(`mutation ($id: String!, $name: String!) {
			shareBookNonUser (id: $id, name: $name) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
			}
		}`, {
			id: id,
			name: name,
		})
	},

	return: async id =>
	{
		return await api(`mutation ($id: String!) {
			returnBook (id: $id) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
			}
		}`, {
			id: id,
		})
	},

	borrow: async id =>
	{
		return await api(`mutation ($id: String!) {
			borrowBook (id: $id) {
				__typename
				...on BookTagDoesNotExistError { message }
				...on BookCannotBeShared { message }
			}
		}`, {
			id: id,
		})
	},

	edit: async (id, changes) =>
	{
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
	}
}