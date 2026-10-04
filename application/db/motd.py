"""application.db.motd"""

from bson.objectid import ObjectId
from pymongo.collection import Collection

from application.exceptions import MotdDoesNotExist
from application.types import Motd

## A pointer to the motd collection in the database.
db: Collection = None  # type: ignore[assignment]


def parse_motd(data: dict) -> Motd:
	"""
	Parse a dict into a Motd TypedDict.

	Args:
		data (dict): The dict data.

	Return:
		Motd: A guaranteed valid Motd TypedDict.
	"""

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


def list_motd(start: int, count: int) -> list[Motd]:
	"""
	Get a paginated list of MOTD items.

	Args:
		start (int): The starting index for pagination.
		count (int): The number of items to retrieve.

	Returns:
		list[Motd]: A list of MOTD items.
	"""
	return [parse_motd(item) for item in db.find({}).skip(start).limit(count)]


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
		id (str): The ID of the MOTD.

	Returns:
		Motd: The deleted MOTD.

	Raises:
		MotdDoesNotExist: If a MOTD does not exist with the given ID.
	"""

	item = db.find_one({'_id': ObjectId(id)})
	if item is None:
		raise MotdDoesNotExist

	db.delete_one({'_id': ObjectId(id)})
	return parse_motd(item)


def update_motd(id: str, text: str) -> Motd:
	"""
	Update the text of a Message of the Day.

	Args:
		id (str): The ID of the MOTD.
		text (str): The new text of the MOTD.

	Returns:
		Motd: The updated MOTD.

	Raises:
		MotdDoesNotExist: If a MOTD does not exist with the given ID.
	"""

	ct = db.update_one({'_id': ObjectId(id)}, {'$set': {'text': text}}).modified_count
	if ct == 0:
		raise MotdDoesNotExist

	return parse_motd({
		'_id': ObjectId(id),
		'text': text,
	})
