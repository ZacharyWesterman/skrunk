export default {
	__user_list: {
		all: null,
		group: null,
	},

	list: async (filter, use_cache = true, restrict = true) => {
		let res
		const sublist = restrict ? 'group' : 'all'
		if (query.users.__user_list[sublist] === null || !use_cache) {
			res = await api(`query ($restrict: Boolean!) {
				listUsers (restrict: $restrict) {
					username
					display_name
				}
			}`, {
				restrict: restrict,
			})
			query.users.__user_list[sublist] = res
		}
		else
			res = query.users.__user_list[sublist]
		return (filter ? res.filter(filter) : res).map(i => { return { value: i.username, display: i.display_name } })
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
