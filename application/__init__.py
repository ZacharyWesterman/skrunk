"""application"""

import ariadne
from flask import Flask
from ariadne.contrib.federation.schema import make_federated_schema
from typing import Any

from .resolvers import query, mutation
from .db.users import count_users
from .scalars import scalars
from .db import init_db, setup_db
from . import routes


def init(*, no_auth=False, blob_path=None, data_db_url='') -> Flask:
	"""
	Initialize the application.

	Parameters:
		no_auth (bool): Flag to disable authentication. Default is False.
		blob_path (str, optional): Path to the blob storage. Default is None.
		data_db_url (str): URL to the database. Default is an empty string.

	Returns:
		Flask: The initialized Flask application instance.
	"""
	init_db(data_db_url, blob_path)

	application: Any = Flask(__name__)
	application.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000  # 5GB file size limit for uploads

	type_defs = ariadne.load_schema_from_path('application/schema')
	application.schema = make_federated_schema(type_defs, [query, mutation] + scalars)

	application.is_initialized = count_users() > 0
	application.no_auth = no_auth
	application.blob_path = blob_path

	# Create temporary admin user if server hasn't been set up yet
	if not application.is_initialized:
		setup_db()

	routes.init(application)

	print('Application has finished initializing.', flush=True)

	return application
