export default {
	users: async () => {
		return await api(`{
			getWeatherUsers {
				username
				lat
				lon
				max {
					disable
					default
					value
				}
				min {
					disable
					default
					value
				}
				last_sent
				exclude
			}
		}`)
	},

	last_execution: async () => {
		return await api(`{
			getLastWeatherExec {
				timestamp
				users
				error
			}
		}`)
	},
}
