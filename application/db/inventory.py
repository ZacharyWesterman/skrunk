from application.tokens import decode_user_token, get_request_token
from . import users
from datetime import datetime
import markdown, html

db = None

def create_inventory_item(category: str, type: str, location: str, blob_id: str, description: str) -> dict:
	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	item = {
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'category': category,
		'type': type,
		'location': location,
		'blob_id': blob_id,
		'description': description,
		'description_html': markdown.markdown(description, output_format = 'html'),
	}

	db.items.insert_one(item)

	return item
