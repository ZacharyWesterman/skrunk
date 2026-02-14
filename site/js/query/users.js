export default {
	__user_list: {
		all: null,
		group: null,
		books: null,
	},

	list: async (filter, use_cache = true, restrict_to_group = true) => {
		let res
		const sublist = restrict_to_group ? 'group' : 'all'
		if (query.users.__user_list[sublist] === null || !use_cache) {
			res = await api(`query ($restrict: Boolean!) {
				listUsers (restrict: $restrict) {
					username
					display_name
				}
			}`, {
				restrict: restrict_to_group,
			})
			query.users.__user_list[sublist] = res
		}
		else
			res = query.users.__user_list[sublist]
		return (filter ? res.filter(filter) : res).map(i => { return { value: i.username, display: i.display_name } })
	},

	list_with_books: async (use_cache = true) => {
		if (query.users.__user_list.books === null || !use_cache) {
			query.users.__user_list.books = await api(`query {
				listUsersWithBooks {
					username
					display_name
				}
			}`)
		}

		return query.users.__user_list.books
			.map(i => { return { value: i.username, display: i.display_name } })
			.sort((a, b) => a.display.localeCompare(b.display))
	},

	sessions: async username => {
		return await api(`query ($username: String!) {
			countSessions (username: $username)
		}`, {
			username: username,
		})
	},

	get: async username => {
		return await api(`query ($username: String!){
			getUser(username:$username) {
				__typename
				...on UserData {
					username
					theme {
						colors {
							name
							value
						}
						sizes {
							name
							value
						}
					}
					perms
					last_login
					display_name
					groups
					disabled_modules
					email
					failed_logins
					is_locked
					disabled
				}
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			username: username
		})
	},
}
