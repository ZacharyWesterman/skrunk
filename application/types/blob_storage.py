"""application.types.blob_storage"""

__all__ = ['BlobStorage', 'BlobPreview', 'BlobThumbnail', 'blob_path']

from dataclasses import dataclass
from pathlib import Path

## The path to the directory where blobs are stored
blob_path: str | None = None


@dataclass(init=False)
class BlobStorage:
	"""
	A class to represent and manage blob storage paths.
	"""

	## The unique identifier for the blob
	id: str
	## The file extension for the blob
	ext: str

	def __init__(self, id: str, ext: str):
		"""
		Initializes a new instance of the class.

		Args:
			id (str): The identifier for the blob.
			ext (str): The file extension for the blob.
		"""
		## The unique identifier for the blob
		self.id = str(id)
		## The file extension for the blob
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
		"""
		Generate the base name for the blob storage object.

		Returns:
			str: The base name consisting of the object's ID and its extension.
		"""
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
	"""

	def __init__(self, id: str, ext: str):
		"""
		Initializes a new instance of the class.

		Args:
			id (str): The identifier for the instance.
			ext (str): The extension to be appended to the identifier.
		"""
		super().__init__(f'{id}_p' if ext != '' else str(id), ext)


class BlobThumbnail(BlobStorage):
	"""
	A subclass of BlobStorage that represents a thumbnail version of a blob.
	These thumbnails are even smaller and lower quality than previews, and thus much faster to load.
	"""

	def __init__(self, id: str, ext: str):
		"""
		Initializes a new instance of the class.

		Args:
			id (str): The identifier for the instance.
			ext (str): The extension associated with the instance. If the extension is not an empty string, the identifier will be suffixed with '_t'.
		"""
		super().__init__(f'{id}_t' if ext != '' else str(id), ext)
