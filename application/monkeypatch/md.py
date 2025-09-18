"""
Adjust Markdown to handle line breaks in lists and other edge cases.
"""

__all__ = []

import re
from xml.etree.ElementTree import Element

import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor

old_markdown = markdown.markdown


class PreListLineBreaks(Preprocessor):
	"""
	A preprocessor class that modifies a list of lines by adding a blank line 
	before list items that are preceded by non-list lines. This ensures proper 
	formatting for list items in markdown or similar text formats.

	Methods:
		run(lines: list[str]) -> list[str]:
			Processes the input lines and inserts blank lines where necessary 
			to separate list items from preceding non-list lines.

	Example:
		Input:
			[
				"This is a paragraph.",
				"- Item 1",
				"- Item 2"
			]
		Output:
			[
				"This is a paragraph.",
				"",
				"- Item 1",
				"- Item 2"
			]
	"""

	def run(self, lines: list[str]) -> list[str]:
		"""
		Processes a list of strings by adding a line break before list items 
		that are preceded by non-list lines.

		Args:
			lines (list[str]): A list of strings representing lines of text.

		Returns:
			list[str]: The modified list of strings with added line breaks 
			where necessary.

		Notes:
			- A "list item" is identified as a line starting with a bullet 
			  point ('-' or '*') or a numbered list format (e.g., '1.').
			- If a line is not a list item and the following line is a list 
			  item, a blank line is inserted between them.
		"""
		# Add a line break before list items that are preceded by non-list lines
		for i in range(len(lines) - 1):
			if (
				not re.match(r'^\s*(-|\*[^\*])|^\s*\d+\.', lines[i])
				and re.match(r'^\s*[-*]\s|^\s*\d+\.', lines[i + 1])
			):
				lines.insert(i + 1, '')
		return lines


class ExternalLinkPreprocessor(Preprocessor):
	"""
	A preprocessor class that modifies lines to ensure that external links are indicated as external.

	Methods:
		run(lines: list[str]) -> list[str]:
			Processes the input lines and modifies external links to include some extra html on the end.
	"""

	def __init__(self) -> None:
		super().__init__()
		self.search_pattern = re.compile(r'(\[.*?\]\(https?://[^\s)]+\))')

	def run(self, lines: list[str]) -> list[str]:
		"""
		Processes a list of strings by modifying external links to include an indicator.

		Args:
			lines (list[str]): A list of strings representing lines of text.

		Returns:
			list[str]: The modified list of strings with external link indicators.
		"""
		for i, line in enumerate(lines):
			# Check for external links in markdown format [text](http://example.com)
			if self.search_pattern.search(line):
				lines[i] = self.search_pattern.sub(r'\1<i class="fa-solid fa-link"></i>', line)
		return lines


class LinkTreeprocessor(Treeprocessor):
	"""
	A postprocessor class that modifies generated html links
	to ensure that external links open in a new tab.
	"""

	def run(self, root: Element) -> None:
		"""
		Processes the HTML tree by modifying links to include the `target="_blank"` attribute.

		Args:
			root (Element): The root element of the HTML tree.
		"""
		for elem in root.iter('a'):
			if elem.attrib.get('href', '').startswith('http'):
				elem.attrib['target'] = '_blank'


class CustomMarkdownExtension(Extension):
	"""
	A Markdown extension that registers custom preprocessors

	Methods:
		extendMarkdown(md: markdown.Markdown) -> None:
			Registers the all custom preprocessors with the provided Markdown instance.
	"""

	def extendMarkdown(self, md: markdown.Markdown) -> None:
		"""
		Extends the functionality of the provided Markdown instance by registering
		a custom preprocessor.

		Args:
			md (markdown.Markdown): The Markdown instance to extend.
		"""
		md.preprocessors.register(PreListLineBreaks(), 'pre_list_line_breaks', 175)
		md.preprocessors.register(ExternalLinkPreprocessor(), 'external_link_preprocessor', 176)
		md.treeprocessors.register(LinkTreeprocessor(), 'link_tree_processor', 15)


def new_markdown(text: str, **kwargs) -> str:
	"""
	Converts the given text into HTML-formatted Markdown.

	This function wraps around the `old_markdown` function, adding specific
	configurations for the output format and extensions. It ensures that the
	output is in HTML format and applies all desired extensions.

	Args:
		text (str): The input text to be converted to Markdown.
		**kwargs: Additional keyword arguments to be passed to the old markdown function.

	Returns:
		str: The HTML-formatted Markdown output.
	"""
	return old_markdown(
		text,
		**kwargs,
		output_format='html',
		extensions=[CustomMarkdownExtension()]
	)


markdown.markdown = new_markdown
