'use strict'

self.addEventListener('push', event => {
	const promise = self.registration.showNotification('Hello World')
	event.waitUntil(promise)
})