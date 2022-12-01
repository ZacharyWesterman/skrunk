window.weather = {
	get_users: async function() {
		return await api(`{
			getWeatherUsers {
				username
				lat
				lon
				phone
				last_sent
				exclude
			}
		}`)
	},

	create_user: async function(username, lat, lon, phone) {
		const query = `mutation ($userdata: WeatherUserInput!){
			createWeatherUser(userdata: $userdata){
				__typename
				...on BadUserNameError {
					message
				}
				...on InsufficientCreds {
					message
				}
			}
		}`
		const vars = {
			userdata: {
				username: username,
				lat: lat,
				lon: lon,
				phone: phone,
			}
		}
		return await api(query, vars)
	},

	delete_user: async function(username) {
		const query = `mutation ($username: String!){
			deleteWeatherUser(username: $username){
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientCreds {
					message
				}
			}
		}`
		const vars = {
			username: username,
		}
		return await api(query, vars)
	},

	enable_user: async function(username) {
		const query = `mutation ($username: String!){
			enableWeatherUser(username: $username){
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientCreds {
					message
				}
			}
		}`
		const vars = {
			username: username,
		}
		return await api(query, vars)
	},

	disable_user: async function(username) {
		const query = `mutation ($username: String!){
			disableWeatherUser(username: $username){
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientCreds {
					message
				}
			}
		}`
		const vars = {
			username: username,
		}
		return await api(query, vars)
	},

	update_user: async function(username, phone, lat, lon) {
		const query = `mutation ($userdata: WeatherUserInput!){
			updateWeatherUser(userdata: $userdata){
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientCreds {
					message
				}
			}
		}`
		const vars = {
			userdata: {
				username: username,
				lat: lat,
				lon: lon,
				phone: phone,
			}
		}
		return await api(query, vars)
	},
}
