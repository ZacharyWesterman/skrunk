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

let mark_as_read = true

// When the user clicks on the notification, open the notifications in a new tab
self.addEventListener('notificationclick', event => {
	mark_as_read = false

	event.waitUntil(
		clients.openWindow(`/?page=notifications`)
	)
})

// When the user manually swipes away the notification, mark it as read
self.addEventListener('notificationclose', event => {
	// Don't mark as read if the user clicked on the notification
	if (!mark_as_read) {
		mark_as_read = true
		return
	}

	const notif = event.notification

	const promise_chain = api(notif.data, //login token
		`mutation ($id: String!) {
		markNotifAsRead (id: $id)
	}`, {
		id: notif.tag,
	})

	event.waitUntil(promise_chain)
})
