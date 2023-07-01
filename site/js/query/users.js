export default {
	list: async (filter) =>
	{
		const res = await api('{listUsers}')
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
