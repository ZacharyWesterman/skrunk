"""application.types.blob_storage"""

__all__ = ['BlobStorage', 'BlobPreview', 'BlobThumbnail', 'blob_path']

from dataclasses import dataclass
from pathlib import Path

blob_path: str | None = None


@dataclass(init=False)
class BlobStorage:
	"""
	A class to represent and manage blob storage paths.

	Attributes:
		id (str): The unique identifier for the blob.
		ext (str): The file extension for the blob.
		exists (bool): True if the blob exists, False otherwise.

	Methods:
		__init__(id: str, ext: str):
			Initializes a new instance of the class.

		path(create: bool = False) -> str:
			Returns the full path to the blob, optionally creating directories.

		basename() -> str:
			Returns the base name of the blob.
	"""
	id: str
	ext: str

	def __init__(self, id: str, ext: str):
		"""
		Initializes a new instance of the class.

		Args:
			id (str): The identifier for the blob.
			ext (str): The file extension for the blob.
		"""
		self.id = str(id)
		self.ext = str(ext)

	def path(self, *, create: bool = False) -> str:
		"""
		Returns the full path to the blob, optionally creating directories.

		Args:
			create (bool): If True, the necessary directories will be created if they do not exist.

		Returns:
			str: The full path to the blob.
		"""
		full_path = f'{blob_path}/{self.id[0:2]}/{self.id[2:4]}'
		if create:
			Path(full_path).mkdir(parents=True, exist_ok=True)

		return f'{full_path}/{self.basename()}'

	def basename(self) -> str:
		return f'{self.id}{self.ext}'

	@property
	def exists(self) -> bool:
		"""
		Check if the blob exists in the storage.

		This method constructs the full path of the blob using its ID and checks
		if a file with the blob's basename exists at that path.

		Returns:
			bool: True if the blob exists, False otherwise.
		"""
		full_path = f'{blob_path}/{self.id[0:2]}/{self.id[2:4]}'
		return Path(f'{full_path}/{self.basename()}').exists()


class BlobPreview(BlobStorage):
	"""
	A subclass of BlobStorage that represents a preview version of a blob.
	These previews are smaller and lower quality than the original.

	Attributes:
		id (str): The identifier for the blob.
		ext (str): The file extension for the blob.
		exists (bool): True if the preview exists, False otherwise.

	Methods:
		__init__(id: str, ext: str): Initializes a BlobPreview instance with a modified id if an extension is provided.
	"""
	def __init__(self, id: str, ext: str):
		super().__init__(f'{id}_p' if ext != '' else str(id), ext)


class BlobThumbnail(BlobStorage):
	"""
	A subclass of BlobStorage that represents a thumbnail version of a blob.
	These thumbnails are even smaller and lower quality than previews, and thus much faster to load.

	Attributes:
		id (str): The identifier for the blob.
		ext (str): The file extension for the blob.
		exists (bool): True if the preview exists, False otherwise.

	Methods:
		__init__(id: str, ext: str): Initializes a BlobThumbnail instance with a modified id if an extension is provided.
	"""
	def __init__(self, id: str, ext: str):
		super().__init__(f'{id}_t' if ext != '' else str(id), ext)
