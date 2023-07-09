export default {
	__user_list: null,

	list: async (filter, use_cache = true) =>
	{
		let res
		if (query.users.__user_list === null || !use_cache)
		{
			res = await api('{listUsers}')
			query.users.__user_list = res
		}
		else
			res = query.users.__user_list
		return filter ? res.filter(filter) : res
	},

	sessions: async username =>
	{
		return await api(`query ($username: String!) {
			countSessions (username: $username)
		}`, {
			username: username,
		})
	},

	get: async username =>
	{
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
