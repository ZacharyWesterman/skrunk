"""
This module initializes the Flask application and sets up the database.

It includes the application configuration, schema loading, and route initialization.
"""

import argparse
from typing import Any

import ariadne
from ariadne.contrib.federation.schema import make_federated_schema
from flask import Flask

from . import bundler, db, monkeypatch, routes, tokens
from .db import init_db, setup_db
from .db.users import count_users
from .resolvers import mutation, query
from .scalars import scalars


def init(*, no_auth: bool = False, blob_path: str | None = None, preview_path: str | None = None, thumbnail_path: str | None = None, database_url: str = '') -> Flask:
	"""
	Initialize the application and database.

	Parameters:
		no_auth (bool, optional): Flag to disable authentication. Default is False.
		blob_path (str, optional): Path to the blob storage. Default is None.
		preview_path (str, optional): Path to where blob previews are stored. If None, defaults to the same as blob_path.
		thumbnail_path (str, optional): Path to where blob thumbnails are stored. If None, defaults to the same as preview_path.
		database_url (str, optional): URL to the database. Default is an empty string.

	Returns:
		Flask: The initialized Flask application instance.
	"""

	if preview_path is None:
		preview_path = blob_path
	if thumbnail_path is None:
		thumbnail_path = preview_path

	tokens.init()

	init_db(database_url, blob_path, preview_path, thumbnail_path)

	application: Any = Flask(__name__)

	# 5GB file size limit for uploads
	application.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000

	type_defs = ariadne.load_schema_from_path('application/schema')
	application.schema = make_federated_schema(type_defs, [query, mutation] + scalars)

	application.is_initialized = count_users() > 0
	application.no_auth = no_auth
	application.blob_path = blob_path
	application.preview_path = preview_path
	application.thumbnail_path = thumbnail_path

	# Create temporary admin user if server hasn't been set up yet
	if not application.is_initialized:
		setup_db()

	routes.init(application)

	print('Application has finished initializing.', flush=True)

	return application


def new(name: str) -> tuple[argparse.Namespace, Flask]:
	parser = argparse.ArgumentParser(
		prog=name,
	)

	parser.add_argument(
		'--blob-path', action='store', default=None, type=str, help='The blob data storage location'
	)
	parser.add_argument(
		'--preview-path', action='store', default=None, type=str,
		help='The storage location for blob previews, if different from main blob storage'
	)

	parser.add_argument('--prod', action='store_true', help='Run in production mode')
	parser.add_argument('--no-auth', action='store_true', help='Disable authentication')
	parser.add_argument(
		'--ip', action='store', default='0.0.0.0', type=str, help='The IP address to bind to'
	)
	parser.add_argument('--port', action='store', default=5000, type=int, help='The port to bind to')
	parser.add_argument('--https', action='store_true', help='Enable HTTPS')
	parser.add_argument(
		'--database', action='store', default='mongodb://localhost:27017/', type=str,
		help='The connection URI of the mongodb database'
	)
	parser.add_argument(
		'--bundle', action='store_true',
		help='Bundle common files to improve performance.'
	)

	args = parser.parse_args()

	if args.blob_path is None and args.preview_path is not None:
		print('ERROR: `--preview-path` flag used but `--blob-path` not specified!')
		exit(1)

	if args.bundle:
		bundler.bundle()
	else:
		bundler.no_bundle()

	app = init(
		no_auth=args.no_auth,
		blob_path=args.blob_path,
		database_url=args.database,
		preview_path=args.preview_path,
	)

	return args, app
