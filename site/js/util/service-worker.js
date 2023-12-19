'use strict'

self.addEventListener('push', event => {
	const promise = self.registration.showNotification(event.data.text())
	event.waitUntil(promise)
})