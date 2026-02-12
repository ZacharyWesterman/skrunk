class RankedChoice extends HTMLElement {
	constructor() {
		super()
	}

	get value() {
		const val = []
		for (const child of this.children) {
			val.push(child.value)
		}
		return val
	}

	connectedCallback() {
		let funcs = [
			'onchange'
		].map(i => {
			const fn = this[i]
			delete this[i]
			return [i, fn]
		}).filter(i => i)
		let triggers = [
			'*change',
			'*bind',
		].map(i => {
			const fn = this.getAttribute(i)
			this.removeAttribute(i)
			return [i.replace('*', '__'), fn]
		}).filter(i => i[1])

		for (const child of this.children) {
			const upButton = document.createElement('i')
			const downButton = document.createElement('i')
			upButton.classList.add('fa-solid', 'fa-caret-up', 'fa-xl', 'rank-direction')
			downButton.classList.add('fa-solid', 'fa-caret-down', 'fa-xl', 'rank-direction')
			child.appendChild(downButton)
			child.appendChild(upButton)

			downButton.onclick = () => {
				if (child.nextElementSibling) {
					this.insertBefore(child.nextElementSibling, child)
					setTimeout(() => $.flash(child), 50)
					if (downButton.onchange) downButton.onchange()
				}
			}

			upButton.onclick = () => {
				if (child.previousElementSibling) {
					this.insertBefore(child, child.previousElementSibling)
					setTimeout(() => $.flash(child), 50)
					if (upButton.onchange) upButton.onchange()
				}
			}

			for (const i of funcs) {
				upButton[i[0]] = i[1]
				downButton[i[0]] = i[1]
			}
			for (const i of triggers) {
				downButton.setAttribute(i[0], i[1])
				upButton.setAttribute(i[0], i[1])
			}
		}
	}
}

customElements.define('ranked-choice', RankedChoice)
