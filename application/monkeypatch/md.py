"""
Adjust Markdown to handle line breaks in lists and other edge cases.
"""

__all__ = []

import re

import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

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


class PreListLineBreaksExtension(Extension):
	"""
	A Markdown extension that registers a custom preprocessor to handle
	line breaks before list elements.

	Methods:
		extendMarkdown(md: markdown.Markdown) -> None:
			Registers the `PreListLineBreaks` preprocessor with the given
			Markdown instance.
	"""

	def extendMarkdown(self, md: markdown.Markdown) -> None:
		"""
		Extends the functionality of the provided Markdown instance by registering
		a custom preprocessor.

		Args:
			md (markdown.Markdown): The Markdown instance to extend.
		"""
		md.preprocessors.register(PreListLineBreaks(), 'pre_list_line_breaks', 175)


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
		extensions=[PreListLineBreaksExtension()]
	)


markdown.markdown = new_markdown
