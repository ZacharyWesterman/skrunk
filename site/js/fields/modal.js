/**
 * Open a dialog box to show information or prompt the user for a choice.
 *
 * Config is an object of the form:
 * {
 * 	type: "info", "error", or "question",
 * 	icon: any string (refer to font-awesome icons),
 * 	title: the title of the modal (large text),
 * 	text: the body text, can be arbitrary HTML,
 * 	buttons: ['Yes', 'No', 'Cancel', 'OK', etc],
 * 	no_cancel: if true, remove the "X" button in the top right of the modal.
 * }
 * Note that all fields in the above object are optional.
 *
 * @param {object} config The modal configuration.
 * @param {function(): void} onload Run this function when the modal opens.
 * @param {function(string): boolean} validate Run this function when the user clicks any button (except the X button). Only closes the modal if this returns true.
 * @param {function(string): any} transform Change the output text when the modal returns.
 * @returns {Promise<any>} A promise that resolves when a selection is made, or rejects if the X button is pressed.
 */
async function modal(config, onload = () => { }, validate = choice => true, transform = choice => choice) {
	await _('modal', config)
	onload()
	$('modal-window').close()
	$('modal-window').showModal()
	$('modal-window-expand').classList.add('expanded')

	return new Promise((resolve, reject) => {
		modal.awaiting = {
			resolve: resolve,
			reject: reject,
			validate: validate,
			transform: transform,
		}

		modal.is_open = true
	})
}

///No modals are open when this src loads.
modal.is_open = false

/**
 * Close the currently open modal. This is identical to the user clicking the X button.
 */
modal.cancel = () => {
	$('modal-window-expand').classList.remove('expanded')
	setTimeout(() => { $('modal-window').close() }, 200)
	modal.awaiting.reject()
	modal.is_open = false
}

/**
 * Close the modal and return a value back to the waiting process.
 * This will behave as if the user clicked a button containing the given value.
 *
 * @param {any} value The value to return from the modal.
 */
modal.return = value => {
	if (typeof value === 'string') value = value.toLowerCase()

	const retn = () => {
		$('modal-window-expand').classList.remove('expanded')
		setTimeout(() => {
			$('modal-window').close()
			modal.awaiting.resolve(modal.awaiting.transform(value))
			modal.is_open = false
		}, 200)
	}

	//Don't close the modal if any fields in it were invalid.
	if (modal.awaiting.validate?.constructor?.name === 'AsyncFunction' || typeof modal.awaiting.validate.then === 'function') {
		modal.awaiting.validate(value).then(res => {
			if (res) retn()
		})
	}
	else {
		if (modal.awaiting.validate(value)) retn()
	}
}

/**
 * Open a dialog box that allows users to select and upload files.
 * @returns A promise that will resolve to a list of uploaded files.
 */
modal.upload = async function () {
	await _('upload_modal', {})
	$('modal-upload-window').close()
	$('modal-upload-window').showModal()
	$('modal-upload-expand').classList.add('expanded')

	//Once modal has loaded, inject list of tags.
	let tagList = $('modal-tag-list')
	tagList.innerHTML = ''
	modal.upload.tag_list = []

	async function tagHTML(tag) {
		const ct = await api(`query ($tag: String!) { countBlobTagUses (tag: $tag) }`, { tag: tag })
		return `<div class="tag clickable ${ct ? '' : 'emphasis'}">${tag} (${ct})\&nbsp;<b>\&times;</b></div>`
	}

	function tagClicks(tagList) {
		const kids = tagList.children
		for (let i = 0; i < kids.length; ++i) {
			const child = kids[i]
			const ix = i
			child.onclick = () => {
				modal.upload.tag_list.splice(ix, 1)
				tagList.removeChild(child)
				tagClicks(tagList)
			}
		}
		if (kids.length === 0) tagList.innerHTML = '<i class="suppress">Automatic tags only</i>'
	}
	tagClicks(tagList)

	//when submitting a tag
	const tagSubmit = async field => {
		const tag = field.value.trim()
		if (tag.length === 0) return

		if (!modal.upload.tag_list.includes(tag)) {
			if (modal.upload.tag_list.length === 0) tagList.innerHTML = ''
			modal.upload.tag_list.push(tag)
			tagList.innerHTML += await tagHTML(tag)
		}

		field.value = ''
		tagClicks(tagList)
	}

	$('modal-tag-input').nextElementSibling.onclick = () => tagSubmit($('modal-tag-input'))
	$.on.enter($('modal-tag-input'), tagSubmit)

	return new Promise((resolve, reject) => {
		modal.upload.awaiting = {
			resolve: resolve,
			reject: reject,
		}
	})
}

/**
 * Close the currently open upload modal. This is identical to the user cancelling the upload(s).
 */
modal.upload.return = () => {
	$('modal-upload-expand').classList.remove('expanded')
	setTimeout(() => { $('modal-upload-window').close() }, 200)

	if (api.upload.cancel()) {
		modal({
			type: 'error',
			title: 'Upload Canceled',
			text: 'All pending file uploads have been stopped.',
			buttons: ['OK'],
		}).catch(() => { })

		modal.upload.awaiting.reject(modal.upload.blobs)
	}
	else {
		modal.upload.awaiting.resolve(modal.upload.blobs)
	}
	return modal.upload.blobs
}

/**
 * Start uploading the files selected in the upload modal.
 * @returns {void}
 */
modal.upload.start = async function () {
	const auto_unzip = $('modal-unpack-check').checked
	const hidden = $('modal-hidden-check').checked
	modal.upload.promises = []
	const tag_list = modal.upload.tag_list
	modal.upload.blobs = []

	async function do_upload(file, dom_progress) {
		const blobs = await api.upload(file, progress => {
			const percent = (progress.loaded / progress.total) * 100
			dom_progress.value = percent
			dom_progress.nextSibling.innerText = parseInt(percent) + '%'
		}, auto_unzip, tag_list, hidden)
		$.hide(dom_progress.parentElement, true)

		if (blobs) {
			modal.upload.blobs.push(...blobs)
		}
	}

	const files = $('modal-file').files

	//make sure all files are <=10GB (max file size limit for uploads)
	let too_big = []
	for (let file of files) {
		if (file.size > (5 * 1000 * 1000 * 1000))
			too_big.push(`${file.name} (${format.file_size(file.size)})`)
	}

	if (too_big.length > 0) {
		const amt = too_big.length === 1 ? 'file exceeds' : 'files exceed'
		const amt2 = too_big.length === 1 ? 'that file' : 'those files'

		await _.modal({
			type: 'error',
			title: 'Ow, right in the bandwidth!',
			text: `<p>For the sake of performance, there's a <b>5GB</b> limit on file uploads.<br>The following ${amt} this limit:</p><i>${too_big.join('<br>')}</i><p>If you really need to upload ${amt2}, I suggest using an FTP client.`,
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	//Show a warning if files are >=50MB (may take a long time)
	let large_files = []
	for (let file of files) {
		if (file.size >= (50 * 1000 * 1000))
			large_files.push(`${file.name} (${format.file_size(file.size)})`)
	}

	if (large_files.length > 0) {
		const header = large_files.length === 1 ? 'a very large file' : 'some very large files'
		const msg = large_files.length === 1 ? 'A file' : 'Some of the files'
		const it_them = large_files.length === 1 ? 'it' : 'them'
		const res = await _.modal({
			title: `<span class="emphasis">WARNING:</span> You're about to upload ${header}!`,
			text: `<p>${msg} you've selected may take a very long time to upload:</p><i>${large_files.join('<br>')}</i><p>This is still under the hard limit of <b>5GB</b> per file, so you <i>can still upload ${it_them}</i>, but if you have a slow or spotty connection you may want to consider uploading a different way.<br><br><b>Do you want to go ahead and upload?</b></p>`,
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (res !== 'yes') return
	}

	//Hide the upload controls so the user can't change them while uploading.
	$.toggle_expand('modal-upload-body', false)
	await sleep(300)

	//Add a progress bar for each file to be uploaded.
	let innerHTML = '<h3>Upload in Progress</h3>'
	innerHTML += '<p>When complete, a message will pop up<br>telling you that the upload is finished.<hr>Click the <b style="font-size: 28px;">&times;</b> button at any time to cancel the upload.<hr></p>'
	for (let i = 0; i < files.length; ++i) {
		innerHTML += `<div><progress id="upload-progressbar-${i}" value="0" max="99"></progress><span></span></div>`
	}
	$('upload-progress').innerHTML = innerHTML
	$.show('upload-progress', true)

	try {
		let promises = []
		for (let i = 0; i < files.length; ++i) {
			let dom_progress = $('upload-progressbar-' + i)
			promises.push(do_upload(files[i], dom_progress))
		}
		modal.upload.promises = promises

		for (const p of promises) {
			await p
		}

		modal({
			icon: 'circle-check',
			title: 'Success!',
			text: 'All files have been uploaded successfully.',
			buttons: ['OK']
		}).catch(() => { })
	}
	catch (xfer) {
		modal.error(xfer.text)
	}

	modal.upload.promises = []
	modal.upload.return()
}

/**
 * Show some options if they're applicable to the file(s) being uploaded.
 */
modal.upload.activate = () => {
	$('modal-button').disabled = false
	function zip_exists() {
		const files = $('modal-file').files
		for (let i = 0; i < files.length; ++i) {
			if (files[i].name.endsWith('.zip')) return true
		}
		return false
	}
	$.toggle('modal-auto-unpack', zip_exists())
	$.show('modal-hide-file')
}

modal.upload.drop_file = event => {
	const area = document.getElementById('drag-drop-zone')
	area.classList.remove('emphasis')
	area.style.backgroundColor = _.css.get_var('--suppress-text')
	setTimeout(() => {
		area.style.backgroundColor = ''
	}, 150)

	event.preventDefault()

	const data = new DataTransfer()
	if (event.dataTransfer.items) {
		// Use DataTransferItemList interface to access the file(s)
		[...event.dataTransfer.items].forEach((item, i) => {
			// If dropped items aren't files, reject them
			if (item.kind === "file") {
				data.items.add(item.getAsFile())
			}
		})
	} else {
		// Use DataTransfer interface to access the file(s)
		[...event.dataTransfer.files].forEach((file, i) => {
			data.items.add(file)
		})
	}

	//Append files to file input
	document.getElementById('modal-file').files = data.files
	modal.upload.activate()
}

modal.upload.drag_file = event => {
	const area = document.getElementById('drag-drop-zone')
	area.classList.add('emphasis')
	event.preventDefault()
}

modal.upload.undrag_file = event => {
	const area = document.getElementById('drag-drop-zone')
	area.classList.remove('emphasis')
	event.preventDefault()
}

/**
 * Briefly show a checkmark animation on screen.
 * This can be used to indicate to the user that an action was successful.
 */
modal.checkmark = () => {
	setTimeout(() => {
		$('action-checkmark').classList.remove('checkmark')
	}, 1000)
	$('action-checkmark').classList.add('checkmark')
}

/**
 * A small helper function for opening a very common type of dialog box, a "something went wrong" message.
 * @param {string} text The error message.
 * @param {string} title The title for this error message.
 * @returns {string} A promise that resolves when the modal is closed.
 */
modal.error = async (text, title = 'ERROR') => {
	return await _.modal({
		type: 'error',
		title: title,
		text: text,
		buttons: ['OK'],
	}).catch(() => 'ok')
}

/**
 * A helper function for opening a modal to await scanning an RFID tag or QR code.
 * @returns {String|null} The scanned or detected QR/RFID code, or null if no code detected.
 */
modal.scanner = async () => {
	modal.scanner._awaiting = true
	const res = await _.modal({
		icon: 'brands fa-nfc-symbol',
		title: 'Ready to scan',
		text: api.snippit('rfid_waiting'),
		buttons: EnabledModules.includes('qr') ? [['Use QR', '<i class="fa-solid fa-qrcode"></i> Use QR'], 'Cancel'] : ['Cancel'],
	}, () => {
		const field = $('rfid_manual_input')
		field.onchange = () => {
			// Make sure this doesn't get called again!
			delete field.onchange
			_.modal.return(field.value)
		}

		function keep_focus() {
			if (modal.scanner._awaiting) {
				if (!document.hasFocus() || field !== document.activeElement) {
					field.readOnly = true
					field.focus()
					setTimeout(() => { field.readOnly = false }, 50)
				}
				setTimeout(keep_focus, 200)
			}
		}

		keep_focus()
	}).catch(() => 'cancel')

	modal.scanner._awaiting = false

	if (res === 'cancel') return null

	if (res === 'use qr') {
		const qrcode = await qr.load_and_process()
		if (qrcode === null) return null
		return $.enforce.hex(qrcode)
	}

	return res
}
modal.scanner._awaiting = false


modal.image = async (url, model3d = false) => {
	await _('image-view-modal', {
		url: url,
		model3d: model3d,
	})

	$('image-window-modal').close()
	$('image-window-modal').showModal()
	$('image-window-expand').classList.add('expanded')

	$(model3d ? 'image-modal-close' : 'image-window-modal').onclick = () => {
		$('image-window-expand').classList.remove('expanded')
		setTimeout(() => { $('image-window-modal').close() }, 200)
	}
}

modal.model3d = async (url) => {
	await modal.image(url, true)
}

modal.tags = async (tag_list, tagQueryName) => {
	async function tagHTML(tag) {
		const ct = await api(`query ($tag: String!) { ${tagQueryName} (tag: $tag) }`, { tag: tag })
		return `<div class="tag clickable ${ct ? '' : 'emphasis'}">${tag} (${ct})\&nbsp;<b>\&times;</b></div>`
	}

	//Query tags all async, then wait for them all to return.
	let promises = []
	for (const tag of tag_list) {
		promises.push(tagHTML(tag))
	}
	for (const p of promises) { await p }

	const res = await modal({
		title: 'Update Tags',
		text: await api.snippit('tag-modal'),
		buttons: ['OK', 'Cancel'],
	}, async () => {
		//Once modal has loaded, inject list of tags.
		let tagList = $('modal-tag-list')
		let innerHTML = ''
		for (const p of promises) { innerHTML += await p }

		tagList.innerHTML = innerHTML

		function tagClicks(tagList) {
			const kids = tagList.children
			for (let i = 0; i < kids.length; ++i) {
				const child = kids[i]
				const ix = i
				child.onclick = () => {
					tag_list.splice(ix, 1)
					tagList.removeChild(child)
					tagClicks(tagList)
				}
			}
		}
		tagClicks(tagList)

		//when submitting a tag
		const tagSubmit = async field => {
			const tag = field.value.trim()
			if (tag.length === 0) return

			if (!tag_list.includes(tag)) {
				tag_list.push(tag)
				tagList.innerHTML += await tagHTML(tag)
			}

			field.value = ''
			tagClicks(tagList)
		}

		$('modal-tag-input').nextElementSibling.onclick = () => tagSubmit($('modal-tag-input'))
		$.on.enter($('modal-tag-input'), tagSubmit)
	}).catch(() => 'cancel')

	if (res === 'cancel') {
		throw 'Cancelled tag selection.'
	}

	return tag_list
}

modal.download_zip = async (size_fn, zip_fn) => {
	const size = await size_fn()

	if (size.__typename !== 'BlobCount') {
		_.modal.error(size.message)
		return
	}

	const res = await _.modal({
		title: 'Download all matching current query?',
		text: `This will create a zip file containing <b>${format.file_size(size.count)}</b> of file data, which will then be downloaded to your device.<br><br>Depending on your network speed and the amount of files involved, this may take a while.`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (res !== 'yes') return

	//Get a unique ID for the pending ZIP action
	const uid = await api(`{ generateUID }`)
	let do_polling = true
	let cancelled = false

	//Show a spinner so users know to wait for the ZIP archive to be generated.
	_.modal({
		title: 'Creating ZIP Archive, Please be Patient...'.replaceAll(' ', '&nbsp;'),
		text: '<div id="progress" style="width:300px;max-width:100%"></div><div style="height: 10rem; align-items: center;"><i class="gg-spinner" style="transform: scale(5,5); left: 47%; top: 50%;"></i></div>',
	}, () => {
		//On load.

		//Begin polling for progress of the ZIP archive.
		async function poll() {
			if (!do_polling) return

			const res = await api(`query ($uid: String!) {
				pollZipProgress(uid: $uid) {
					__typename
					...on ZipProgress { progress item finalizing }
					...on BlobDoesNotExistError { message }
				}
			}`, {
				uid: uid,
			})

			if (res.__typename !== 'ZipProgress') {
				console.warn('ZIP Progress: ' + res.message)
				return
			}

			const field = $('progress')
			if (!field) return

			if (res.finalizing) {
				field.innerHTML = `Finalizing ZIP Archive...`
				return
			}

			field.innerHTML = `Progress: <span class="emphasis">[${(res.progress * 100).toFixed(0)}%]</span><br>Item: <span class="suppress">${res.item}</span>`

			if (!do_polling) return

			//Schedule another poll later
			setTimeout(poll, 100)
		}

		setTimeout(poll, 2000) //Start polling after user has been waiting for a while.
	}).catch(() => {
		//Cancel the zip action
		cancelled = true
		do_polling = false
		api(`mutation ($uid: String!) { cancelZipArchive (uid: $uid) { __typename } }`, {
			uid: uid,
		})
	})

	const zip = await zip_fn(uid)
	do_polling = false

	if (cancelled) {
		_.modal({
			title: 'ZIP&nbsp;Cancelled.',
			buttons: ['OK'],
		}).catch(() => { })
		return
	}

	if (zip.__typename !== 'Blob') {
		_.modal.error(zip.message)
		return
	}

	//Now that ZIP has been created, download it
	let link = document.createElement('a')
	link.download = `${zip.name}${zip.ext}`
	link.href = `/download/${zip.id}${zip.ext}`
	link.target = '_blank'
	link.click()

	await _.modal({
		icon: 'circle-check',
		title: 'ZIP Archive Created',
		text: 'The ZIP archive has been created and will now download to your device.<hr>The archive file will be kept for 24 hours.<br>If you\'d like to download it again before then,<br>go to the <b><i class="fa-solid fa-hard-drive"></i> Files</b> page and click "Include ephemeral files".',
		buttons: ['OK'],
	})
}

export default modal
