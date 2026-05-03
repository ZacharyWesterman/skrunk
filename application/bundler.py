"""
This module handles the (optional) bundling of site files, which can improve performance
by decreasing the number of HTTP requests needed to load content.
"""

from pathlib import Path
from jsmin import jsmin
from rcssmin import cssmin
import json
import re

CSS_URL = re.compile(r'@import +url\( *[\'"]([^\'"]*)[\'"] *\) *;')
JS_IMPORT = re.compile(r'\bimport +((\w+) +from *)?[\'"]([^\'"]*)[\'"]')
JS_EXPORT = re.compile(r'\bexport *default\b')
JS_FUNC_IMPORT = re.compile(r'\bimport *\( *[\'"]([^\'"]*)[\'"] *\)')


def bundle_css(path: str) -> None:
	"""
	Resolve all imports in a CSS file and bundle into
	a single (minified) monolithic file.

	Args:
		path (str): The path to the file.
	"""

	with open(path, 'r', encoding='utf8') as fp:
		text = fp.read()

	found = True
	while found:
		found = False
		insertions = []
		for i in CSS_URL.finditer(text):
			span = i.span()
			url = i.group(1)
			insertions += [(span, url)]
			found = True

		for (span, url) in reversed(insertions):
			with open('site/' + url, 'r', encoding='utf8') as fp:
				text = text[:span[0]] + fp.read() + text[span[1] + 1:]

	with open('site/bundled/' + Path(path).name, 'w', encoding='utf8') as fp:
		# Minify the CSS before outputting
		fp.write(cssmin(text))  # type: ignore


def bundle_js(path: str) -> None:
	"""
	Resolve all imports in a JS file and bundle into
	a single (minified) monolithic file.

	Args:
		path (str): The path to the file.
	"""

	with open(path, 'r', encoding='utf8') as fp:
		text = fp.read()

	# Replace statements like `import name from url` or `import url`
	insertions = []
	for i in JS_IMPORT.finditer(text):
		span = i.span()
		name = i.group(2)
		url = i.group(3)
		insertions += [(span, name, url)]

	for (span, name, url) in reversed(insertions):
		with open(str(Path(path).parent / url), 'r', encoding='utf8') as fp:
			if name is not None:
				imported_text = (
					'const ' + name + ' = (() => {\n' +
					JS_EXPORT.sub('return ', fp.read()) +
					'})()\n'
				)
			else:
				imported_text = fp.read()

			text = text[:span[0]] + imported_text + text[span[1]:]

	# Replace statements like `import(url)`
	insertions = []
	for i in JS_FUNC_IMPORT.finditer(text):
		span = i.span()
		url = i.group(1)
		insertions += [(span, url)]

	for (span, url) in reversed(insertions):
		with open('site/' + url, 'r', encoding='utf8') as fp:
			imported_text = (
				'(async () => { return { default: (() => {\n' +
				JS_EXPORT.sub('return ', fp.read()) +
				'})() } })()'
			)
			text = text[:span[0]] + imported_text + text[span[1]:]

	with open('site/bundled/' + Path(path).name, 'w', encoding='utf8') as fp:
		# Minify the JS before outputting
		fp.write(jsmin(text, quote_chars='\'"`'))


def bundle() -> None:
	"""
	Bundle all relevant site files.
	"""

	print('Bundling source for performance...', end='', flush=True)
	Path('site/bundled').mkdir(exist_ok=True)

	# Bundle and minify certain files
	with open('data/bundle_files.txt', 'r', encoding='utf8') as fp:
		for line in fp.readlines():
			filename = line.strip()
			ext = Path(filename).suffix
			if ext == '.css':
				bundle_css(filename)
			elif ext == '.js':
				bundle_js(filename)

	def flat_iter(path: Path):
		if path.is_file():
			yield path
		else:
			for i in path.iterdir():
				yield from flat_iter(i)

	# Bundle other files into packs for site pre-loading
	for i in ['config', 'html', 'templates']:
		data = {}
		for file in flat_iter(Path(f'site/{i}')):
			if i == 'config' and file.suffix != '.json':
				continue

			if not file.is_file():
				continue

			with open(str(file), 'r', encoding='utf8') as fp:
				filename = str(file).replace('site/', '')
				data[filename] = json.dumps(json.load(fp)) if file.suffix == '.json' else fp.read()

		with open(f'site/bundled/{i}.json', 'w', encoding='utf8') as fp:
			json.dump(data, fp)

	print(' Done.', flush=True)


def no_bundle() -> None:
	"""
	Remove any bundled files, if they exist.
	"""

	bundle_dir = Path('site/bundled')
	if bundle_dir.exists():
		for i in bundle_dir.iterdir():
			i.unlink()
		bundle_dir.rmdir()


def get_bundled_path(path: str) -> str | None:
	"""
	Get the path of the bundled version of a file, if any.

	Args:
		path (str): The path of the non-bundled version of the file.

	Returns:
		str | None: The path of the bundled version of the file,
			or None if no bundled version exists.
	"""

	bundled_path = Path('site/bundled') / Path(path).name
	return str(bundled_path) if bundled_path.exists() else None
