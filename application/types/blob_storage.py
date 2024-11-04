__all__ = ['BlobStorage', 'BlobPreview', 'BlobThumbnail']

from dataclasses import dataclass
from pathlib import Path

@dataclass
class BlobStorage:
	id: str
	ext: str

	def path(self, *, create: bool = False) -> str:
		global blob_path
		full_path = f'{blob_path}/{self.id[0:2]}/{self.id[2:4]}'
		if create:
			Path(full_path).mkdir(parents=True, exist_ok=True)

		return f'{full_path}/{self.basename()}'

	def basename(self) -> str:
		return f'{self.id}{self.ext}'

	@property
	def exists(self) -> bool:
		full_path = f'{blob_path}/{self.id[0:2]}/{self.id[2:4]}'
		return Path(f'{full_path}/{self.basename()}').exists()
	
class BlobPreview(BlobStorage):
	def __init__(self, id: str, ext: str):
		super().__init__(f'{id}_p' if ext != '' else str(id), ext)

class BlobThumbnail(BlobStorage):
	def __init__(self, id: str, ext: str):
		super().__init__(f'{id}_t' if ext != '' else str(id), ext)
