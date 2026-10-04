"""application.db.motd"""

from bson.objectid import ObjectId
from pymongo.collection import Collection

from application.exceptions import MotdDoesNotExist
from application.types import Motd

## A pointer to the motd collection in the database.
db: Collection = None  # type: ignore[assignment]


def parse_motd(data: dict) -> Motd:
	return Motd(
		_id=data['_id'],
		id=str(data['_id']),
		text=data['text']
	)


def get_motd(id: str) -> Motd:
	"""
	Get the Message of the Day by ID.

	Args:
		id (str): The ID of the MOTD.

	Returns:
		Motd: The associated MOTD.

	Raises:
		MotdDoesNotExistError: If there is no such MOTD with the given ID.
	"""

	item = db.find_one({'_id': ObjectId(id)})

	if item is None:
		raise MotdDoesNotExist

	return parse_motd(item)


def get_nth_motd(index: int) -> Motd:
	"""
	Get the Message of the Day by index.

	Args:
		index (int): The index of the MOTD.

	Returns:
		Motd: The associated MOTD.

	Raises:
		MotdDoesNotExistError: If the index is out of bounds.
	"""

	for item in db.find({}).skip(index):
		return parse_motd(item)

	raise MotdDoesNotExist


def count_motd() -> int:
	"""
	Count the total number of MOTD items.

	Returns:
		int: The total MOTD count.
	"""
	return db.count_documents({})


def create_motd(text: str) -> Motd:
	"""
	Create a new Message of the Day.

	Args:
		text (str): The text for the MOTD.

	Returns:
		Motd: The resultant MOTD.
	"""

	motd_id = db.insert_one({'text': text}).inserted_id
	return parse_motd({'_id': motd_id, 'text': text})


def delete_motd(id: str) -> Motd:
	"""
	Delete a Message of the Day.

	Args:
		id (std): The ID of sthe MOTD.

	Returns:
		Motd: The deleted MOTD.

	Raises:
		MotdDoesNotExist: If an MOTD does not exist with the given ID.
	"""

	item = db.find_one({'_id': ObjectId(id)})
	if item is None:
		raise MotdDoesNotExist

	db.delete_one({'_id': ObjectId(id)})
	return parse_motd(item)
