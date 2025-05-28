
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
	mobile: ((a) => /android|(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4)) || /KF/.test(a))(navigator.userAgent || navigator.vendor || window.opera),

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
	get page() { return environment.get_param('page') },

	/**
	 * Get the value of a URL param.
	 * @param {string} name The key of the param.
	 * @returns {string} The param value.
	 */
	get_param: name => {
		const value = (new URLSearchParams(location.search)).get(name)
		return value && decodeURIComponent(value)
	},

	/**
	 * Change the value of a URL param.
	 * @param {string} name The key of the param.
	 * @param {string} value The new value.
	 */
	set_param: (name, value) => {
		let params = {}
		const url = new URLSearchParams(location.search)
		url.forEach((value, key) => { params[key] = value })

		params[name] = value
		let text = ''
		for (const i in params) {
			if (params[i]) {
				text += (text ? '&' : '?') + i + '=' + encodeURIComponent(params[i])
			}
		}

		window.history.replaceState({}, '', text || '/')
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
	get max_displayed_pages() {
		const rem_px = parseFloat(getComputedStyle(document.documentElement).fontSize)
		const max_width = Math.min(window.innerWidth / rem_px - 4, 900 / rem_px) - 5
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
		let ct = Math.floor((lookups.max_displayed_pages - 1) / 2)

		if (index + ct >= total) {
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
		let ct = Math.ceil((lookups.max_displayed_pages) / 2)

		if (index - ct < 0) {
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
	file_size: size => {
		const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'EB']
		let this_size = 0
		while (size > 1000) {
			size /= 1000
			this_size += 1
		}

		return `${size.toFixed(2)}&nbsp;${sizes[this_size]}`
	},
}

class Color {
	constructor(r, g, b) {
		this.r = r
		this.g = g
		this.b = b

		this.toString = () => {
			return '#' + this.r.toString(16).padStart(2, '0') + this.g.toString(16).padStart(2, '0') + this.b.toString(16).padStart(2, '0')
		}

		this.lerp = (other, ratio) => {
			const lerp = (a, b, ratio) => Math.floor(b + ratio * (a - b))

			return new Color(
				lerp(this.r, other.r, ratio),
				lerp(this.g, other.g, ratio),
				lerp(this.b, other.b, ratio),
			)
		}
	}
}
Color.fromHex = (hex) => {
	const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)

	const r = parseInt(result[1], 16)
	const g = parseInt(result[2], 16)
	const b = parseInt(result[3], 16)

	return new Color(r, g, b)
}
window.Color = Color

/**
 * Helper functions for displaying chart data.
 */
window.chart = {
	create: async (field, chart_config) => {
		await import('/js/libs/chart.js')
		Chart.defaults.color = _.css.get_var('--secondary-text')

		if ($(field).children.length) {
			if ($(field).children[0].c) $(field).children[0].c.destroy()
			$(field).children[0].remove()
		}

		let canvas = document.createElement('canvas')
		$(field).appendChild(canvas)

		canvas.c = new Chart(canvas, chart_config)
	},

	/**
	 * Draw a bar chart in the given element.
	 * @param {string} field The ID, name, or object of the DOM element to inject the chart into.
	 * @param {string[]} labels The labels for each bar.
	 * @param {number[]} data The height values of each bar.
	 */
	bar: async (field, labels, data, horizontal = false) => {
		const grid_color = _.css.get_var('--secondary')
		const bar_color = Color.fromHex(_.css.get_var('--emphasis-text'))

		chart.create(field, {
			type: 'bar',
			data: {
				labels: labels,
				datasets: [{
					data: data,
					borderWidth: 0,
					backgroundColor: bar_color,
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
							color: grid_color,
						},
						border: {
							color: grid_color,
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

	/**
	 * Draw a pie chart in the given element.
	 * @param {string} field The ID, name, or object of the DOM element to inject the chart into.
	 * @param {string[]} labels The labels for each bar.
	 * @param {number[]} data The height values of each bar.
	 */
	pie: async (field, labels, data, percents = true) => {
		const total = data.reduce((a, b) => a + b)

		chart.create(field, {
			type: 'pie',
			data: {
				labels: labels,
				datasets: [{
					data: data,
					tooltip: {
						callbacks: {
							label: context => {
								return percents ? `${context.raw} (${Math.floor(context.raw * 100 / total)}%)` : context.raw
							},
						},
					},
				}],
			},
			options: {
				plugins: {
					legend: {
						position: 'bottom',
					},
					title: {
						display: percents,
						text: 'Total: ' + total,
					},
				},
			},
		})
	},
}

/**
 * Helper functions for handling QR codes.
 */
window.qr = {
	crop_image: (canvas, file, startX, startY, endX, endY) => {
		return new Promise(resolve => {
			//Resize canvas to full image, then crop
			const ctx = canvas.getContext('2d')

			const image = new Image()
			const reader = new FileReader()
			reader.onload = event => {
				image.src = event.target.result
			}
			reader.readAsDataURL(file)

			ctx.drawImage(image, 0, 0, image.width, image.height)

			console.log(image.width, image.height, canvas.width, canvas.height)

			if (startX !== undefined && startY !== undefined && endX !== undefined && endY !== undefined) {
				if (startX > endX) endX = [startX, startX = endX][0]
				if (startY > endY) endY = [startY, startY = endY][0]

				let scaleX = 1
				let scaleY = 1
				if (image.width > canvas.width) {
					scaleX = image.width / canvas.width
					scaleY = image.height / canvas.height
				}

				const cropWidth = (endX - startX) * scaleX
				const cropHeight = (endY - startY) * scaleY
				const croppedImage = ctx.getImageData(startX * scaleX, startY * scaleY, cropWidth, cropHeight)

				canvas.width = cropWidth
				canvas.height = cropHeight
				ctx.putImageData(croppedImage, 0, 0)
			}

			canvas.toBlob(blob => {
				resolve(new File([blob], 'QR.png'))
			}, 'image/png')
		})
	},

	upload_image: async () => {
		const file = await api.file_prompt('image/*', false, 'camera')
		let blob_upload = null
		let startX, startY, endX, endY, isDragging = false

		const img_choice = await _.modal({
			title: '<span id="qr-title">Image Preview</span>',
			text: '<span id="text">Touch and drag to crop image.<span><br><canvas id="canvas"></canvas>',
			buttons: ['OK', 'Cancel'],
		}, () => {
			//On load, fill the canvas with the image data.
			const canvas = $('canvas')
			const ctx = canvas.getContext('2d')

			const image = new Image()
			image.onload = () => {
				canvas.width = Math.min(window.innerWidth, image.width)
				canvas.height = Math.min(window.innerHeight, image.height)

				const scale_factor = Math.min(canvas.width / image.width, canvas.height / image.height)
				const new_width = image.width * scale_factor
				const new_height = image.height * scale_factor

				canvas.width = new_width
				canvas.height = new_height

				ctx.drawImage(image, 0, 0, new_width, new_height)
			}

			canvas.addEventListener('mousedown', e => {
				startX = e.offsetX
				startY = e.offsetY
				isDragging = true
			})

			canvas.addEventListener('mousemove', (e) => {
				if (isDragging) {
					endX = e.offsetX
					endY = e.offsetY
					drawOverlayAndRectangle(startX, startY, endX, endY)
				}
			})

			canvas.addEventListener('mouseup', e => {
				isDragging = false
			})

			// Handle touch events for cropping
			canvas.addEventListener('touchstart', (e) => {
				const touch = e.touches[0]
				const rect = canvas.getBoundingClientRect()
				startX = touch.clientX - rect.left
				startY = touch.clientY - rect.top
				isDragging = true
			})

			canvas.addEventListener('touchmove', e => {
				if (isDragging) {
					e.stopPropagation()
					e.preventDefault()

					const touch = e.touches[0]
					const rect = canvas.getBoundingClientRect()

					endX = touch.clientX - rect.left
					endY = touch.clientY - rect.top
					drawOverlayAndRectangle(startX, startY, endX, endY)
				}

			})

			canvas.addEventListener('touchend', () => {
				isDragging = false
			})

			// Draw overlay and cropping rectangle
			const drawOverlayAndRectangle = (startX, startY, endX, endY) => {
				ctx.clearRect(0, 0, canvas.width, canvas.height)
				image.onload()

				if (startX !== undefined && startY !== undefined && endX !== undefined && endY !== undefined) {
					ctx.fillStyle = 'rgba(128, 128, 128, 0.5)'  // semi-transparent gray

					if (startX > endX) endX = [startX, startX = endX][0]
					if (startY > endY) endY = [startY, startY = endY][0]

					// Draw the overlay
					ctx.fillRect(0, 0, canvas.width, startY)
					ctx.fillRect(0, startY, startX, endY - startY)
					ctx.fillRect(endX, startY, canvas.width - endX, endY - startY)
					ctx.fillRect(0, endY, canvas.width, canvas.height - endY)

					// Draw the cropping rectangle
					ctx.strokeStyle = 'red'
					ctx.lineWidth = 2
					ctx.strokeRect(startX, startY, endX - startX, endY - startY)
				}
			}

			const reader = new FileReader()
			reader.onload = event => {
				image.src = event.target.result
			}
			reader.readAsDataURL(file)
		}, choice => {
			if (choice !== 'ok') return true

			//Resize canvas to full image, then crop
			const canvas = $('canvas')
			const ctx = canvas.getContext('2d')

			const image = new Image()
			const reader = new FileReader()
			reader.onload = event => {
				image.src = event.target.result
			}
			reader.readAsDataURL(file)

			ctx.drawImage(image, 0, 0, image.width, image.height)


			if (startX !== undefined && startY !== undefined && endX !== undefined && endY !== undefined) {
				if (startX > endX) endX = [startX, startX = endX][0]
				if (startY > endY) endY = [startY, startY = endY][0]

				let scaleX = 1
				let scaleY = 1
				if (image.width > canvas.width) {
					scaleX = image.width / canvas.width
					scaleY = image.height / canvas.height
				}

				const cropWidth = (endX - startX) * scaleX
				const cropHeight = (endY - startY) * scaleY
				const croppedImage = ctx.getImageData(startX * scaleX, startY * scaleY, cropWidth, cropHeight)

				canvas.width = cropWidth
				canvas.height = cropHeight
				ctx.putImageData(croppedImage, 0, 0)
			}

			canvas.toBlob(blob => {
				blob_upload = new File([blob], 'QR.png')
			}, 'image/png')

			return true
		})

		if (img_choice !== 'ok') return null

		if (blob_upload === null) {
			_.modal.error('No file selected!')
			return null
		}

		return blob_upload
	},

	capture_image: () => {
		return new Promise((resolve, reject) => {
			const video = $('camera-video')
			const canvas = $('camera-canvas')

			async function init_camera() {
				try {
					const stream = await navigator.mediaDevices.getUserMedia({
						video: { facingMode: 'environment' },
						audio: false
					});
					video.srcObject = stream
					return true
				} catch (err) {
					console.info("Camera access denied or not available.")
					return false
				}
			}

			function take_photo() {
				return new Promise(resolve => {
					//Get the file
					const context = canvas.getContext('2d')
					canvas.width = video.videoWidth
					canvas.height = video.videoHeight
					context.drawImage(video, 0, 0, canvas.width, canvas.height)

					new Promise(res => {
						canvas.toBlob(blob => {
							res(new File([blob], 'QR.png'))
						}, 'image/png')
					}).then(file => {

						const reticle = $('camera-reticle').getBoundingClientRect()
						const container = $('camera-container').getBoundingClientRect()

						//Get the bounds of the reticle
						const top = (reticle.top) / container.height * canvas.height
						const left = reticle.left / container.width * canvas.width
						const right = reticle.right / container.width * canvas.width
						const bottom = (reticle.bottom) / container.height * canvas.height

						qr.crop_image(canvas, file, left, top, right, bottom).then(result_file => {
							console.log("Captured image:", result_file)
							resolve(result_file)
						})
					})
				})
			}

			init_camera().then(cameraAllowed => {
				if (!cameraAllowed) {
					reject('Camera access denied or not available.')
					return
				}

				$.show('camera-container')
				$.focus('camera-reticle')

				$('camera-container').onclick = async () => {
					const blob_upload = await take_photo()

					$.unfocus()
					$.hide('camera-container')

					// Remove camera stream to stop it from running in the background
					if (video.srcObject) {
						const tracks = video.srcObject.getTracks()
						tracks.forEach(track => track.stop())
						video.srcObject = null
					}

					// Remove click handler to prevent multiple captures
					$('camera-container').onclick = () => { }

					resolve(blob_upload)
				}
			})
		})
	},

	/**
	 * Upload an image to the server and process it as a QR code, then delete the image.
	 * If no QR code was found, this function returns null.
	 * @returns {Promise<string?>} The text that the QR code contained.
	 */
	load_and_process: async () => {
		let qrcode = null
		let blob_upload = null

		try {
			while (true) {
				const res = await new Promise((resolve, reject) => {
					qr.capture_image().then(file => {
						const reader = new FileReader()
						reader.onload = () => {
							_.modal({
								type: 'question',
								title: 'QR Code Capture',
								text: `
									Does this image look correct?<br>
									<img src="${reader.result}" style="max-width: 100%; max-height: 100%;" />
								`,
								buttons: ['Yes', 'No', 'Cancel'],
							}).then(choice => {
								if (choice === 'cancel') {
									resolve(false) // User cancelled the image capture
									return
								}
								resolve((choice === 'yes') ? file : null)
							}).catch(() => {
								reject('Image capture cancelled.')
							})
						}
						reader.readAsDataURL(file)

					}).catch(reject)
				})

				// If the user confirmed the image, upload it
				if (res) {
					blob_upload = res
					break
				}

				// If the user cancelled, break the loop
				if (res === false) {
					break
				}
			}
		} catch (e) {
			blob_upload = await qr.upload_image().catch(() => null)
		}

		// If the user cancelled the image upload, return null
		if (blob_upload === null) {
			return null
		}

		// Upload the image to the server and process it as a QR code.

		await _.modal({
			title: '<span id="qr-title">Uploading QR Code...</span>',
			text: '<div style="height: 10rem; align-items: center;"><i class="gg-spinner" style="transform: scale(5,5); left: 45%; top: 50%;"></i></div><progress id="upload-progressbar-qr" value="0" max="100"></progress>',
			no_cancel: true,
		}, async () => { //On modal load

			const upload_res = await api.upload(blob_upload, progress => {
				const percent = progress.loaded / progress.total
				$('upload-progressbar-qr').value = percent
			}, false, [], false, true)

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

			for (const blob of upload_res) {
				// mutate.blobs.delete(blob.id)
			}

			if (res.error !== null) {
				_.modal.cancel()
				setTimeout(() => { _.modal.error(res.error) }, 300)
				return
			}

			qrcode = res.data

			_.modal.return()
		}).catch(() => { })

		return qrcode
	},

	/**
	 * Generate a QR code, and prompt the user to download the resultant image.
	 * @param {string} text The text the QR code should contain. If not given, defaults to the file's UUID.
	 */
	generate: async (text = null) => {
		let amount = 1
		if (text === null) {
			amount = await _.modal({
				title: 'Generate QR Code',
				text: api.snippit('qr_input'),
				buttons: ['OK', 'Cancel'],
			}, () => {
				//On load
				$.bind('amount', () => {
					$.valid('amount', $('amount').validity.valid)
				})
			}, choice => {
				//Validate
				return choice !== 'ok' || $('amount').validity.valid
			}, choice => {
				//Transform on submit
				return (choice === 'ok') ? parseInt($.val('amount')) : choice
			}).catch(() => 'cancel')

			if (amount === 'cancel') return
		}

		const blob_data = await api(`
		mutation ($text: String, $amount: Int!) {
			getBlobFromQR (text: $text, amount: $amount) {
				__typename
				...on Blob { id ext }
				...on InsufficientPerms { message }
			}
		}`, { text: text, amount: amount })

		if (blob_data.__typename !== 'Blob') {
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
	const padding = '='.repeat((4 - base64String.length % 4) % 4)
	const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/')

	const rawData = window.atob(base64)
	const outputArray = new Uint8Array(rawData.length)

	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i)
	}
	return outputArray
}

/**
 * Helper functions for handling push notifications.
 */
window.push = {
	get supported() {
		return ('serviceWorker' in navigator) && ('PushManager' in window)
	},
	get permission_given() {
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

		if (push.permission !== 'granted') {
			console.log('Push notification permission was not granted. Result: ', push.permission)
			$.show('no-notifications')
			push.__resolve()
			return false
		}

		return true
	},

	register: async () => {
		if (push.permission !== 'granted') return false

		try {
			push.registration = await navigator.serviceWorker.register('/js/util/service-worker.js')
		}
		catch (e) {
			console.warn('Failed to create service worker:', e)
			$.show('no-notifications')
			push.__resolve()
			return false
		}

		if (push.registration) {
			await push.registration.update()
			let sub = await push.registration.pushManager.getSubscription()
			if (sub) {
				push.subscription = sub
				push.subscribed = true
				push.__resolve()
			}
			else {
				$.show('no-notifications')
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

		try {
			push.subscription = await push.registration.pushManager.subscribe(config)
		}
		catch (e) {
			_.modal.error(`Unable to enable web notifications on this browser.<hr><div class="emphasis">${e}</div>`)
			return false
		}

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

		if (res.__typename !== 'Notification') {
			_.modal.error(res.message)
			await push.subscription.unsubscribe()
			push.subscription = null
			$.show('no-notifications')
			push.__resolve()
			return false
		}

		push.subscribed = true
		push.__resolve()
		$.hide('no-notifications', true)

		return true
	},

	unsubscribe: async () => {
		if (!push.registration) return

		let subscription = await push.registration.pushManager.getSubscription()
		if (subscription) {
			const auth = JSON.parse(JSON.stringify(subscription)).keys.auth
			const res = await api(`mutation ($auth: String!) {
				deleteSubscription(auth: $auth)
			}`, {
				auth: auth,
			})
			subscription.unsubscribe()
			push.subscription = null
			push.subscribed = false
		}

		$.show('no-notifications')
	},

	send: async (title, body, username) => {
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
			username: username || api.username,
			title: title,
			body: body,
			category: null,
		})

		if (res.__typename !== 'Notification') {
			_.modal.error(res.message)
			return
		}
	},

	show_notifs: async () => {
		return api(`query ($username: String!, $read: Boolean!) {
			countNotifications (username: $username, read: $read)
		}`, {
			username: api.username,
			read: false,
		}).then(async notif_ct => {
			await push.ready

			if (notif_ct) {
				if (push.subscribed) $.show('yes-notifications')
				$('notif-count').innerText = notif_ct
				$.show('notif-count')
				$('notif-icon').onclick = () => {
					dashnav('notifications')
				}
			}
			else {
				if (push.subscribed) $.hide('yes-notifications', true)
				$('notif-icon').onclick = () => { }
				$.hide('notif-count', true)
			}
		})
	},
}

push.ready = new Promise(resolve => {
	push.__resolve = resolve
})

//Automatically enable push notifications if the user has already given permission.
if (push.permission_given) {
	push.enable().then(push.register)
}
else {
	push.__resolve()
	$.show('no-notifications')
}
