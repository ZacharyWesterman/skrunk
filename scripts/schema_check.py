#!/usr/bin/env python3
# This script just validates the GraphQL schema,
# to make sure the application doesn't immediately crash on startup.

import ariadne

if __name__ == '__main__':
	try:
		type_defs = ariadne.load_schema_from_path('application/schema')
	except Exception as e:
		print(f"\033[31mError loading schema:\033[0m {e}")
		exit(1)

	try:
		schema = ariadne.make_executable_schema(type_defs)
	except Exception as e:
		print(f"\033[31mError making schema executable:\033[0m {e}")
		exit(1)
