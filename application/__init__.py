import ariadne
from flask import Flask
from ariadne.contrib.federation import make_federated_schema

from .resolvers import query, mutation
from .db.users import count_users
from .scalars import scalars
from .db import init_db, setup_db
from . import routes

def init(*, no_auth = False, blob_path = None, data_db_url = ''):
	init_db(data_db_url, blob_path)

	application = Flask(__name__)
	application.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000 #5GB file size limit for uploads

	type_defs = ariadne.load_schema_from_path('application/schema')
	application.schema = make_federated_schema(type_defs, [query, mutation] + scalars)

	application.is_initialized = count_users() > 0
	application.no_auth = no_auth
	application.blob_path = blob_path

	#Create temporary admin user if server hasn't been set up yet
	if not application.is_initialized:
		setup_db()

	routes.init(application)

	print('Application has finished initializing.', flush=True)

	return application
