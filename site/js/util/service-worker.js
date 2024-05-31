'use strict'

function api(login_token, query_string, variables = null) {
	const query_data = {
		'query': query_string,
		'variables': variables,
	}

	return new Promise((resolve, reject) => {
		fetch('/api', {
			method: 'POST',
			mode: 'cors',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${login_token}`,
			},
			body: JSON.stringify(query_data),
		}).then(res => {
			if (res.status >= 200 && res.status < 300 && res.ok) {
				res.json().then(response => {
					for (const elem in response.data) {
						resolve(response.data[elem])
						break
					}
				})
			}
			else {
				reject(res)
			}

		}).catch(res => {
			reject(res)
		})
	})
}

self.addEventListener('push', event => {
	const msg = event.data.json()

	const promise = self.registration.showNotification(msg.title, {
		icon: '/favicon-dark.png',
		body: msg.body,
		tag: msg.notif_id,
		data: msg.login_token,
	})
	event.waitUntil(promise)
})

self.addEventListener('notificationclose', event => {
	const notif = event.notification
	notif.close()

	const promise_chain = api(notif.data, //login token
		`mutation ($id: String!) {
		markNotifAsRead (id: $id)
	}`, {
		id: notif.tag,
	})

	event.waitUntil(promise_chain)
})
