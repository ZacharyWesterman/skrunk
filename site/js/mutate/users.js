export default {
	delete: async username =>
	{
		const query = `
		mutation ($username: String!){
			deleteUser(username: $username) {
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			'username' : username,
		}
		return await api(query, vars)
	},

	create: async (username, pass_hash) =>
	{
		const query = `
		mutation ($username: String!, $password: String!){
			createUser(username: $username, password: $password) {
				__typename
				...on BadUserNameError {
					message
				}
				...on UserExistsError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			'username' : username,
			'password' : pass_hash,
		}
		return await api(query, vars)
	},

	revoke: async username =>
	{
		return await api(`
		mutation ($username: String!) {
			revokeSessions (username: $username)
		}`, {
			username: username,
		})
	},

	permissions: async (username, permission_list) =>
	{
		const query = `
		mutation ($username: String!, $perms: [String!]!){
			updateUserPerms(username: $username, perms: $perms) {
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			'username' : username,
			'perms': permission_list,
		}
	},

	password: async (username, pass_hash) =>
	{
		return await api(`mutation ($username: String!, $password: String!) {
			updateUserPassword(username: $username, password: $password) {
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			username: username,
			password: pass_hash,
		})
	}
}
