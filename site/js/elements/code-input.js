class CodeInput extends HTMLElement {
	constructor() {
		const self = super()
		self.editor = null
	}

	get value() {
		return this.editor?.value ?? ''
	}

	set value(newValue) {
		this.editor?.update({
			value: newValue
		})
	}

	async connectedCallback() {
		const Yace = (await import('/js/libs/yace.js')).default

		const syn = this.getAttribute('syntax')
		if (!syn) {
			console.error('No syntax attribute specified for code-input field!')
			return
		}

		const promise = import(`/js/util/${syn}.js`).catch(() => {
			console.error(`No syntax file for ${syn}!`)
		})

		const syntax = (await promise)?.default
		if (!syntax) {
			console.error(`Failed to read syntax default for ${syn}.`)
			return
		}

		this.editor = new Yace(this, {
			value: this.value ?? '',
			lineNumbers: false,
			highlighter: syntax,
		})
		this.editor.textarea.spellcheck = false

		const updateCallback = () => {
			if (this.onchange) {
				this.onchange()
			}
			if (this.onblur) {
				this.onblur()
			}
			if (this.onclick) {
				this.onclick()
			}
		}

		const placeholder = this.getAttribute('placeholder')
		if (placeholder) {
			const inner = document.createElement('span')
			inner.style.color = 'gray'
			inner.style.fontSize = '80%'
			inner.innerText = placeholder
			const display = this.editor.textarea.nextElementSibling

			function injectPlaceholder() {
				for (const child of display.children) {
					display.removeChild(child)
				}
				display.appendChild(inner)
			}
			injectPlaceholder()

			this.editor.onUpdate(value => {
				if (value === '') {
					injectPlaceholder()
				}
				updateCallback()
			})
		} else {
			this.editor.onUpdate(updateCallback)
		}
	}

	disconnectedCallback() {
		this.editor.destroy()
	}
}

customElements.define('code-input', CodeInput)
