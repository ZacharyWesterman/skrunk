window.safe_html = string => string ? string.replaceAll('\'', '\\\'').replaceAll('"', '&quot;').replaceAll('\n', '\\n') : ''
window.no_line_break = string => string.replaceAll(' ', '&nbsp;').replaceAll('-', '&#8209;')

window.html_encode = string => {
	let elem = document.createElement('textarea')
	elem.innerText = string
	return elem.innerHTML
}

window.html_decode = string => {
	let elem = document.createElement('textarea')
	elem.innerHTML = string
	return elem.value
}

window.image_restrict = string => {
	return string.replaceAll('<img ', '<img style="width:100%; max-width: 400px;" height="auto" ')
}

window.environment = {
	mobile: ((a) => /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))(navigator.userAgent||navigator.vendor||window.opera),
	apple: navigator.userAgent.includes('Macintosh'),
	ios: /iPhone|iPod|iPad/.test(navigator.userAgent),
	page: null,
	set_page: (location, name) => {
		environment.page = name || location
		window.history.replaceState({}, '', (name ? '' : '?page=') + location)
	},
}

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

window.lookups = {
	max_displayed_pages: () => {
		const rem_px = parseFloat(getComputedStyle(document.documentElement).fontSize)
		const max_width = Math.min(window.innerWidth/rem_px - 4, 900/rem_px) - 5
		const max_pages = Math.floor(max_width / 2)

		return max_pages
	},

	prev_pages: (index, total) => {
		let ct = Math.floor(lookups.max_displayed_pages() / 2)

		if (index + ct >= total)
		{
			ct += ct - (total - index) + 1
		}

		return Math.max(index - ct, 0)
	},

	next_pages: (index, total) => {
		let ct = Math.ceil(lookups.max_displayed_pages() / 2)

		if (index - ct < 0)
		{
			ct -= (index - ct) + 1
		}

		return Math.min(index + ct, total)
	},
}


window.format = {
	file_size: size =>
	{
		const sizes = ['B', 'KB', 'MB', 'GB', 'EB']
		let this_size = 0
		while (size > 1000)
		{
			size /= 1000
			this_size += 1
		}

		return `${size.toFixed(2)} ${sizes[this_size]}`
	},
}

window.chart = {
	bar: async (field, labels, data) =>
	{
		await import('https://cdn.jsdelivr.net/npm/chart.js')
		Chart.defaults.color = _.css.get_var('--secondary-text')
		const disabled_text = _.css.get_var('--disabled-text')

		new Chart($(field), {
			type: 'bar',
			data: {
				labels: labels,
				datasets: [{
					data: data,
					borderWidth: 1
				}]
			},
			options: {
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
					},
				}
			}
		})
	},
}

window.qr = {
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
				_.modal({
					type: 'error',
					title: 'ERROR',
					text: res.error,
					buttons: ['OK'],
				}).catch(() => {})
				return
			}

			qrcode = res.data

			_.modal.return()
		}).catch(() => {})

		return qrcode
	},

	generate: async (text = null) =>
	{
		const blob_data = await api('mutation ($text: String) { getBlobFromQR (text: $text) { id ext } }', {text: text})

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
