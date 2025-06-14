"""
This module provides functionality for manipulating PDF documents.
"""

from pdf2image import convert_from_path
from PIL import Image


def create_preview(pdf_path: str, preview_path: str, page_number: int = 0) -> bool:
	"""
	Create a preview image from the first page of a PDF document.

	Args:
		pdf_path (str): The path to the PDF file.
		preview_path (str): The path where the preview image will be saved.
		page_number (int): The page number to create a preview from (default is 0 for the first page).

	Returns:
		bool: True if the preview was created successfully, False otherwise.
	"""

	images = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)
	print(images)
	if images:
		images[0].thumbnail((1024, 1024), Image.Resampling.LANCZOS)
		images[0].save(preview_path)
		return True

	return False
