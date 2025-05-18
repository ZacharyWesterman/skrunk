#!/usr/bin/env python3
# This script builds all GraphQL types into TypedDict classes for use in the application.

from application.integrations.graphql import schema

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
	for i in class_data['params']:
		data_type = type_text(i["type"])
		for j in data_type[1]:
			if j == 'datetime':
				type_imports['datetime'] = 'from datetime import datetime'
			elif j not in builtin_types:
				type_imports[j] = f'from .{j.lower()} import {j}'

		text += f'\t{i["name"]}: {data_type[0]}\n'

	return '\n'.join(type_imports.values()) + '\n\n' + text + '\n'


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


def main():
	types = schema()['types']

	# Build list of unions
	for t in types:
		if not t['union']:
			continue

		unions[t['name']] = t['subtypes']

	for t in types:
		if t['union']:
			continue

		# print(t['name'])

		text = class_text(t)
		with open(f'application/types/{t["name"].lower()}.py', 'w') as f:
			f.write(text)


if __name__ == '__main__':
	main()
