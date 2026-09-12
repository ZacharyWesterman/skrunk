"""application.types.doctype"""


class Doctype:
	"""
	A class to represent supported blob document types.
	"""

	RICHTEXT = 'odt'
	SPREADSHEET = 'ods'

	supported = [
		'.txt', '.md', '.doc', '.docx', '.rtf',
		'.odf', '.odt', '.ods', '.xls', '.xlsx', '.csv',
	]

	sheet_types = ['.ods', '.xls', '.xlsx', '.csv']
