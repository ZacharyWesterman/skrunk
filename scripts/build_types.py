#!/usr/bin/env python3
# This script builds all GraphQL types into TypedDict classes for use in the application.

import sys  # nopep8
import os  # nopep8
sys.path.append(os.path.abspath('.'))  # nopep8

from application.integrations.graphql import schema
from pathlib import Path

type_aliases = {
	'String': 'str',
	'Int': 'int',
	'Float': 'float',
	'Boolean': 'bool',
	'DateTime': 'datetime',
	'Date': 'datetime',
	'PhoneNumber': 'str',
	'Color': 'str',
	'Size': 'str',
	'Long': 'int',
}

builtin_types = [
	'str',
	'int',
	'float',
	'bool',
]

unions: dict[str, list[str]] = {}


def class_text(class_data: dict) -> str:
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
	"""Convert a GraphQL type to a DataClass object definition.
	Args:
		data_type (str): The GraphQL type to convert.
	Returns:
		str: The converted DataClass.
		str: The base type (without any modifiers).
	"""

	if data_type in type_aliases:
		return type_aliases[data_type], [type_aliases[data_type]]
	elif data_type in unions:
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
		return type_text(data_type)

	return data_type + ' | None', [data_type]


def output_types():
	types = schema()['types']

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
		text = class_text(t)

		# Skip if the file already exists and is up to date
		if Path(filename).exists():
			with open(filename, 'r') as f:
				if f.read() == text:
					continue

		print(f'Writing {filename}...')

		with open(filename, 'w') as f:
			f.write(text)


def list_changed_types():
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
		with open(filename, 'r') as f:
			if f.read() != text:
				changed_types.append(t['name'])
				continue

	print(', '.join(sorted(changed_types)))


if __name__ == '__main__':
	if 'check' in sys.argv:
		list_changed_types()
	else:
		output_types()
