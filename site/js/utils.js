
/**
 * Convert text into a format that is safe to inject directly into HTML attribute text.
 * @param {string} text Input text.
 * @returns {string} The converted text.
 */
window.safe_html = text => text ? text.replaceAll('\'', '\\\'').replaceAll('"', '&quot;').replaceAll('\n', '\\n') : ''

/**
 * Replace all breaking characters with their non-breaking variants.
 * @param {string} text Input text.
 * @returns {string} The converted text.
 */
window.no_line_break = text => text.replaceAll(' ', '&nbsp;').replaceAll('-', '&#8209;')

/**
 * HTML-encode text.
 * @param {string} text Input text.
 * @returns {string} The encoded text.
 */
window.html_encode = text => {
	let elem = document.createElement('textarea')
	elem.innerText = text
	return elem.innerHTML
}

/**
 * Decoded HTML-encoded text.
 * @param {string} text Input text.
 * @returns {string} The decoded text.
 */
window.html_decode = string => {
	let elem = document.createElement('textarea')
	elem.innerHTML = string
	return elem.value
}

/**
 * Convert HTML <img> tags to restrict their size to something reasonable.
 * @param {string} text HTML text, possibly containing img tags.
 * @returns {string} The converted text.
 */
window.image_restrict = text => {
	return text.replaceAll('<img ', '<img style="width:100%; max-width: 400px;" height="auto" ')
}

/**
 * Store information about the client device.
 */
window.environment = {
	/**
	 * Whether the client is a mobile device.
	 */
	mobile: ((a) => /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))(navigator.userAgent||navigator.vendor||window.opera),

	/**
	 * Whether the client is an Apple device, but not iOS.
	 */
	apple: navigator.userAgent.includes('Macintosh'),

	/**
	 * Whether the client is running iOS.
	 */
	ios: /iPhone|iPod|iPad/.test(navigator.userAgent),

	/**
	 * The current page per last navigation.
	 */
	page: null,

	/**
	 * Change the name of the page we're on, for example, when navigating to various modules.
	 * @param {string} location The internal name of the page.
	 * @param {string} name The name to display in the tab, next to favicon. Defaults to location if not specified.
	 */
	set_page: (location, name = null) => {
		environment.page = name || location
		window.history.replaceState({}, '', (name ? '' : '?page=') + location)
	},
}

/**
 * Get black or white, whatever would contrast best with the given color.
 * @param {string} hex The hex representation of the color to invert.
 * @returns {string} A monochrome inversion of the given color.
 */
window.invert_color = hex => {
	if (hex.indexOf('#') === 0) {
		hex = hex.slice(1)
	}
	// convert 3-digit hex to 6-digits.
	if (hex.length === 3) {
		hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]
	}
	if (hex.length !== 6) {
		throw new Error('Invalid HEX color.')
	}
	const r = parseInt(hex.slice(0, 2), 16)
	const g = parseInt(hex.slice(2, 4), 16)
	const b = parseInt(hex.slice(4, 6), 16)
	return (r * 0.299 + g * 0.587 + b * 0.114) > 186
		? '#000000'
		: '#FFFFFF'
}

/**
 * Helper functions for lookup pages.
 */
window.lookups = {
	/**
	 * Get the maximum number of page icons that can be displayed at the current window width.
	 * @returns {number} The number of displayable pages.
	 */
	max_displayed_pages: () => {
		const rem_px = parseFloat(getComputedStyle(document.documentElement).fontSize)
		const max_width = Math.min(window.innerWidth/rem_px - 4, 900/rem_px) - 5
		const max_pages = Math.floor(max_width / 2)

		return max_pages
	},

	/**
	 * Get the number of (displayed) pages that came before the current page.
	 * @param {int} index The number of the current page.
	 * @param {int} total The total number of pages there are.
	 * @returns {int} The number of prev pages.
	 */
	prev_pages: (index, total) => {
		let ct = Math.floor(lookups.max_displayed_pages() / 2)

		if (index + ct >= total)
		{
			ct += ct - (total - index) + 1
		}

		return Math.max(index - ct, 0)
	},

	/**
	 * Get the number of (displayed) pages that come after the current page.
	 * @param {int} index The number of the current page.
	 * @param {int} total The total number of pages there are.
	 * @returns The number of next pages.
	 */
	next_pages: (index, total) => {
		let ct = Math.ceil(lookups.max_displayed_pages() / 2)

		if (index - ct < 0)
		{
			ct -= (index - ct) + 1
		}

		return Math.min(index + ct, total)
	},
}

/**
 * Text formatting helper functions.
 */
window.format = {
	/**
	 * Convert a number of bytes into a human-readable format.
	 * @param {int} size The size in bytes.
	 * @returns {string} A human-readable size, rounded to the hundredths place.
	 */
	file_size: size =>
	{
		const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'EB']
		let this_size = 0
		while (size > 1000)
		{
			size /= 1000
			this_size += 1
		}

		return `${size.toFixed(2)}&nbsp;${sizes[this_size]}`
	},
}

/**
 * Helper functions for displaying chart data.
 */
window.chart = {
	/**
	 * Draw a bar chart in the given element.
	 * @param {string} field The ID, name, or object of the DOM element to inject the chart into.
	 * @param {string[]} labels The labels for each bar.
	 * @param {number[]} data The height values of each bar.
	 */
	bar: async (field, labels, data, horizontal = false) =>
	{
		await import('https://cdn.jsdelivr.net/npm/chart.js')
		Chart.defaults.color = _.css.get_var('--secondary-text')
		const disabled_text = _.css.get_var('--disabled-text')

		if ($(field).children.length)
		{
			$(field).children[0].remove()
		}

		let canvas = document.createElement('canvas')
		$(field).appendChild(canvas)

		new Chart(canvas, {
			type: 'bar',
			data: {
				labels: labels,
				datasets: [{
					data: data,
					borderWidth: 1
				}]
			},
			options: {
				indexAxis: horizontal ? 'y' : 'x',
				plugins: {
					legend: {
						display: false
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						grid: {
							color: disabled_text,
						},
						border: {
							color: disabled_text,
						},
						ticks: {
							autoSkip: !horizontal,
						}
					},
					x: {
						ticks: {
							autoSkip: horizontal,
						}
					}
				}
			}
		})

		//Return a helper object that lets you easily update the chart
		let handle = {
			labels: labels,
			data: data,
			horizontal: horizontal,
		}

		handle.update = params => {
			const _labels = params.labels || labels
			const _data = params.data || data
			const _horiz = (params.horizontal !== undefined) ? params.horizontal : horizontal

			chart.bar(field, _labels, _data, _horiz)

			handle.labels = _labels
			handle.data = _data
			handle.horizontal = _horiz
		}

		return handle
	},
}

/**
 * Helper functions for handling QR codes.
 */
window.qr = {
	/**
	 * Upload an image to the server and process it as a QR code, then delete the image.
	 * If no QR code was found, this function throws an exception.
	 * @returns {string} The text that the QR code contained.
	 */
	load_and_process: async () =>
	{
		const file = await api.file_prompt('image/*', false, 'camera')
		let qrcode = null

		await _.modal({
			title: '<span id="qr-title">Uploading QR Code...</span>',
			text: '<div style="height: 10rem; align-items: center;"><i class="gg-spinner" style="transform: scale(5,5); left: 45%; top: 50%;"></i></div><progress id="upload-progressbar-qr" value="0" max="100"></progress>',
			no_cancel: true,
		}, async () => { //On modal load

			const upload_res = await api.upload(file, progress => {
				const percent = progress.loaded / progress.total * 100
				$('upload-progressbar-qr').value = percent
			})

			$.hide('upload-progressbar-qr', true)
			$('qr-title').innerText = 'Processing QR Code...'

			const res = await api(`query ($id: String!) {
				getQRFromBlob (id: $id) {
					data
					error
				}
			}`, {
				id: upload_res[0].id
			})

			for (const blob of upload_res)
			{
				mutate.blobs.delete(blob.id)
			}

			if (res.error !== null)
			{
				_.modal.error(res.error)
				return
			}

			qrcode = res.data

			_.modal.return()
		}).catch(() => {})

		return qrcode
	},

	/**
	 * Generate a QR code, and prompt the user to download the resultant image.
	 * @param {string} text The text the QR code should contain. If not given, defaults to the file's UUID.
	 */
	generate: async (text = null) =>
	{
		const blob_data = await api(`
		mutation ($text: String) {
			getBlobFromQR (text: $text) {
				__typename
				...on Blob { id ext }
				...on InsufficientPerms { message }
			}
		}`, {text: text})

		if (blob_data.__typename !== 'Blob')
		{
			_.modal.error(blob_data.message)
			return
		}

		//Now that QR code image has been created, download it
		let link = document.createElement('a')
		link.download = `${blob_data.id}${blob_data.ext}`
		link.href = `/download/${blob_data.id}${blob_data.ext}`
		link.target = '_blank'
		link.click()

		//Delete the blob when we're done.
		setTimeout(() => {
			mutate.blobs.delete(blob_data.id)
		}, 100)
	},
}

/**
 * Check if the currently logged in user is an admin.
 * Note that changing this does NOT actually give user admin access, just whether admin logic is triggered.
 *
 * @returns {boolean} True if the logged in user has admin permissions.
 */
window.has_perm = id => SelfUserData.perms.includes(id)

function urlB64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - base64String.length % 4) % 4);
	const base64 = (base64String + padding)
		.replace(/\-/g, '+')
		.replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);

	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

/**
 * Helper functions for handling push notifications.
 */
window.push = {
	get supported()
	{
		return ('serviceWorker' in navigator) && ('PushManager' in window)
	},
	get permission_given()
	{
		return push.supported && (Notification.permission === 'granted')
	},
	permission: null,
	subscribed: false,
	registration: null,
	subscription: null,

	enable: async () => {
		if (!push.supported) return false

		//Request permission to send push notifications.
		push.permission = await Notification.requestPermission()

		if (push.permission !== 'granted')
		{
			console.log('Push notification permission was not granted. Result: ', push.permission)
			return false
		}

		return true
	},

	register: async () => {
		if (push.permission !== 'granted') return false

		try
		{
			push.registration = await navigator.serviceWorker.register('/js/util/service-worker.js')
		}
		catch (e)
		{
			console.warn('Failed to create service worker:', e)
			return false
		}

		if (push.registration)
		{
			await push.registration.update()
			let sub = await push.registration.pushManager.getSubscription()
			if (sub)
			{
				push.subscription = sub
				push.subscribed = true
				push.__resolve()
			}
		}

		return true
	},

	subscribe: async () => {
		if (!push.registration) return false

		push.unsubscribe()

		const VAPID = await api('{ getVAPIDPublicKey }')
		const public_key = urlB64ToUint8Array(VAPID)

		const config = {
			userVisibleOnly: true,
			applicationServerKey: public_key,
		}

		push.subscription = await push.registration.pushManager.subscribe(config)

		const res = await api(`mutation ($username: String!, $subscription: SubscriptionToken!) {
			createSubscription(username: $username, subscription: $subscription) {
				__typename
				...on MissingConfig { message }
				...on UserDoesNotExistError { message }
				...on WebPushException { message }
				...on InvalidSubscriptionToken { message }
				...on BadNotification { message }
			}
		}`, {
			username: api.username,
			subscription: push.subscription,
		})

		if (res.__typename !== 'Notification')
		{
			_.modal.error(res.message)
			await push.subscription.unsubscribe()
			push.subscription = null
			return false
		}

		push.subscribed = true
		push.__resolve()

		return true
	},

	unsubscribe: async () => {
		if (!push.registration) return

		let subscription = await push.registration.pushManager.getSubscription()
		if (subscription)
		{
			const auth = JSON.parse(JSON.stringify(subscription)).keys.auth
			const res = await api(`mutation ($auth: String!) {
				deleteSubscription(auth: $auth)
			}`, {
				auth: auth,
			})
			subscription.unsubscribe()
			push.subscription = null
		}
	},

	send: async (title, message) => {

		if (!push.subscription)
		{
			_.modal.error('User is not registered to allow notifications!')
			return
		}

		const res = await api(`mutation ($username: String!, $title: String!, $body: String!, $category: String) {
			sendNotification(username: $username, title: $title, body: $body, category: $category) {
				__typename
				...on MissingConfig { message }
				...on UserDoesNotExistError { message }
				...on WebPushException { message }
				...on InvalidSubscriptionToken { message }
				...on BadNotification { message }
			}
		}`, {
			username: api.username,
			title: 'Yo, this is a test push notification!',
			body: 'This is some body text that is meant to be more descriptive than just the title.',
			category: null,
		})

		if (res.__typename !== 'Notification')
		{
			_.modal.error(res.message)
			return
		}
	},
}

push.ready = new Promise(resolve => {
	push.__resolve = resolve
})

//Automatically enable push notifications if the user has already given permission.
if (push.permission_given)
{
	push.enable().then(push.register)
}
