"""application.types.item"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime
from .usermindata import UserMinData
from .blob import Blob


class Item(TypedDict):
	"""
	A type for describing an arbitrary inventory item.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The unique identifier for the item.
	id: str
	## The date and time when the item was created.
	created: datetime
	## Minimal user data for the creator of the item.
	creator: UserMinData
	## Minimal user data for the owner of the item.
	owner: UserMinData
	## The category of the item, such as 'electronics', 'furniture', etc.
	category: str
	## The type of the item, such as 'laptop', 'chair', etc.
	type: str
	## The location where the item is stored, such as 'office', 'warehouse', etc.
	location: str
	## The blob associated with the item, likely restricted to just an image.
	blob: Blob
	## The raw text description of the item.
	description: str
	## The HTML-rendered version of the item's description.
	description_html: str
	## A list of RFID tags or QR codes associated with the item.
	rfid: list[str]
