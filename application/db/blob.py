from datetime import datetime
import mimetypes
from application.tokens import decode_user_token, get_request_token

db = None

def create_blob(dir: str, name: str, tags: list = []) -> str:
	pos = name.rfind('.')
	ext = name[pos+1::]

	username = decode_user_token(get_request_token()).get('username')

	return db.data.blob.insert_one({
		'created': datetime.now(),
		'name': name[0:pos],
		'ext': ext,
		'mimetype': mimetypes.guess_type(name)[0],
		'tags': tags,
		'creator': username,
	}).inserted_id, ext
