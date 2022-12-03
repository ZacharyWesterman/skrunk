export default {
	phone: function(field)
	{
		$.enforce.phone(field)

		if (field.value.length === 0)
			field.value = field.defaultValue

		if (field.value.length != 10) {
			field.classList.add('invalid')
			return false
		} else {
			field.classList.remove('invalid')
			return true
		}
	},

	number: function(field)
	{
		if (field.validity.valid)
			field.classList.remove('invalid')
		else
			field.classList.add('invalid')

		return field.validity.valid
	},
}
