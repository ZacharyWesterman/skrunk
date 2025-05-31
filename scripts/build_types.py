#!/usr/bin/env python3
# This script builds all GraphQL types into TypedDict classes for use in the application.

import os  # nopep8
import sys  # nopep8

sys.path.append(os.path.abspath('.'))  # nopep8

# pylint: disable=wrong-import-position
from pathlib import Path

from application import exceptions
from application.integrations import exceptions as integration_exceptions
from application.integrations.graphql import schema

# pylint: enable=wrong-import-position

type_aliases = {
	'String!': 'str',
	'Int!': 'int',
	'Float!': 'float',
	'Boolean!': 'bool',
	'DateTime!': 'datetime',
	'Date!': 'datetime',
	'PhoneNumber!': 'str',
	'Color!': 'str',
	'Size!': 'str',
	'Long!': 'int',
}

builtin_types = [
	'str',
	'int',
	'float',
	'bool',
]

unions: dict[str, list[str]] = {}


def class_text(class_data: dict) -> str:
	"""
	Convert a GraphQL type to a TypedDict class definition.

	Args:
		class_data (dict): The GraphQL type data to convert.

	Returns:
		str: The converted TypedDict class definition.
	"""

	type_imports: dict[str, str] = {
		'TypedDict': 'from typing import TypedDict'
	}

	text = f'class {class_data["name"]}(TypedDict):\n'
	# Add any documentation
	docs = class_data['doc'].strip().replace("\n", "\n\t")
	if docs:
		text += f'\t"""\n\t{docs}\n\t"""\n\n'

	for i in class_data['params']:
		data_type = type_text(i["type"])
		for j in data_type[1]:
			if j == 'datetime':
				type_imports['datetime'] = 'from datetime import datetime'
			elif j not in builtin_types:
				type_imports[j] = f'from .{j.lower()} import {j}'

		docs = i['doc'].strip().replace("\n", " ")
		if docs:
			text += f'\t## {docs}\n'
		text += f'\t{i["name"]}: {data_type[0]}\n'

	text = '\n'.join(type_imports.values()) + '\n\n\n' + text
	return text


def type_text(data_type: str) -> tuple[str, list[str]]:
	"""
	Convert a GraphQL type to a DataClass object definition.

	Args:
		data_type (str): The GraphQL type to convert.

	Returns:
		str: The converted DataClass.
		str: The base type (without any modifiers).
	"""

	if data_type in type_aliases:
		return type_aliases[data_type], [type_aliases[data_type]]
	if data_type in unions:
		return ' | '.join(unions[data_type]), unions[data_type]

	if data_type.startswith('['):
		# Remove the brackets
		last_bracket = data_type.rfind(']')
		if last_bracket == -1:
			raise ValueError(f'Invalid type: {data_type}')

		data_type = data_type[1:last_bracket]
		type_info = type_text(data_type)
		return f'list[{type_info[0]}]', type_info[1]

	if data_type.endswith('!'):
		data_type = data_type[0:-1]
		return data_type, [data_type]

	text, types = type_text(data_type + '!')
	return text + ' | None', types


def parse_file_text(name: str, filename: str, text: str) -> tuple[bool, str]:
	"""
	Compare the given text with the contents of a file,
	and return whether the file needs to be updated.

	Args:
		filename (str): The path to the file to check.
		text (str): The text to compare against the file contents.
		file_docstring (str): The docstring to use for the file.

	Returns:
		tuple[bool, str]: A tuple where the first element is True if the file needs to be updated,
		and the second element is the docstring to use for the file.
	"""

	file_docstring = f'"""application.types.{name}"""'

	if not Path(filename).exists():
		print(f'File {filename} does not exist, creating...')
		return True, file_docstring + '\n\n' + text

	with open(filename, 'r', encoding='utf8') as f:
		file_text = f.read()

	# Retain the module docstring if it exists
	if file_text.startswith('"""'):
		index = file_text.find('"""', 3)
		if index != -1:
			file_docstring = '"""' + file_text[3:index] + '"""'
			file_text = file_text[index + 3:].lstrip()

	return file_text != text, file_docstring + '\n\n' + text


def create_init_py(init_py_files: list[str]) -> None:
	"""
	Create the __init__.py file for the types module, importing all types.

	Args:
		init_py_files (list[str]): A list of type names to import in the __init__.py file.
	"""

	init_filename = 'application/types/__init__.py'

	# Retain the module docstring if it exists
	init_py_text = ''
	existing_text = ''
	with open(init_filename, 'r', encoding='utf8') as fp:
		existing_text = fp.read()
		parts = existing_text.split('"""')
		if len(parts) > 1:
			init_py_text += '"""' + parts[1] + '"""\n\n'

	# Sort the imports to satisfy pylint
	for i in sorted((i for i in init_py_files if i[0] == '_'), key=lambda x: x.lower()):
		init_py_text += f'from .{i.lower()} import {i}\n'
	for i in sorted((i for i in init_py_files if i[0] != '_'), key=lambda x: x.lower()):
		init_py_text += f'from .{i.lower()} import {i}\n'

	if existing_text != init_py_text:
		print(f'Writing {init_filename}...')
		with open(init_filename, 'w', encoding='utf8') as fp:
			fp.write(init_py_text)


def output_types() -> None:
	"""Build all GraphQL types into TypedDict classes for use in the application."""

	init_py_files: list[str] = []

	types = schema()['types']

	# Build list of unions
	for t in types:
		if not t['union']:
			continue

		unions[t['name']] = t['subtypes']

	file_list = ['__init__', 'blob_storage']

	# Build list of types
	for t in types:
		if t['union']:
			continue

		# Skip types that are exceptions
		if exceptions.__dict__.get(t['name']):
			continue
		# Skip types that are integration exceptions
		if integration_exceptions.__dict__.get(t['name']):
			continue

		filename = f'application/types/{t["name"].lower()}.py'

		text = class_text(t)

		init_py_files += [t['name']]

		file_list.append(t['name'].lower())

		# Skip if the file already exists and is up to date
		changed, new_text = parse_file_text(t['name'].lower(), filename, text)
		if not changed:
			continue

		print(f'Writing {filename}...')

		with open(filename, 'w', encoding='utf8') as f:
			f.write(new_text)

	# Create the __init__.py file
	if len(init_py_files) > 0:
		create_init_py(init_py_files)

	# Delete any old files that are no longer needed
	for file in Path('application/types').glob('*.py'):
		if file.name[:-3] not in file_list:
			print(f'Deleting {file.name}...')
			file.unlink()


def list_changed_types() -> None:
	"""List all types that have changed since the last build."""

	types = schema()['types']
	changed_types = []

	# Build list of unions
	for t in types:
		if not t['union']:
			continue

		unions[t['name']] = t['subtypes']

	# Build list of types
	for t in types:
		if t['union']:
			continue

		filename = f'application/types/{t["name"].lower()}.py'
		if not Path(filename).exists():
			changed_types.append(t['name'])
			continue

		text = class_text(t)

		if not parse_file_text(t['name'].lower(), filename, text)[0]:
			continue

		changed_types.append(t['name'])

	print(', '.join(sorted(changed_types)))


if __name__ == '__main__':
	if 'check' in sys.argv:
		list_changed_types()
	else:
		output_types()
