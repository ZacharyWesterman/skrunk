'use strict'

self.addEventListener('push', event => {
	const msg = event.data.json()

	const promise = self.registration.showNotification(msg.title, {
		icon: '/favicon-dark.png',
		body: msg.body,
	})
	event.waitUntil(promise)
})