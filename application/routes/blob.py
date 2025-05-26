"""application.routes.blob"""

import json
import mimetypes
import os
import re
from typing import Any, Generator

from flask import Response, jsonify, request

from application.db import blob, perms

from . import auth, files

application: Any = None

CHUNK_SIZE = 1024 * 1024 * 16  # 16 MiB


def file_stream(full_path: str, range_header: str | None) -> Generator[bytes, None, None]:
	"""
	Generator to stream file data in chunks.

	Args:
		full_path (str): The full path to the file to be streamed.

	Yields:
		bytes: Chunks of file data.
	"""
	byte1 = 0
	byte2 = None

	file_size = os.stat(full_path).st_size
	fp = open(full_path, 'rb')

	# Check if the request has a Range header for partial content
	if range_header:
		match = re.search(r'(\d+)-(\d*)', range_header)
		if match:
			groups = match.groups()
			if groups[0]:
				byte1 = int(groups[0])
				fp.seek(byte1)
			if groups[1]:
				byte2 = int(groups[1])

	# Stream the file.
	while True:
		start = 0

		if byte1 < file_size:
			start = byte1
		if byte2:
			length = byte2 + 1 - byte1
		else:
			length = file_size - start

		chunk_size = CHUNK_SIZE if byte1 > 0 else 1024  # 1 KiB for the first chunk
		length = min(length, chunk_size)

		chunk = fp.read(length)
		if not chunk:
			break

		yield chunk

		byte1 += length
		if byte2 is not None:
			byte2 += length

		if byte1 >= file_size:
			break

	fp.close()


def stream(path: str) -> Response:
	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	path = files.sanitize_path(path)

	full_path = blob.BlobStorage(path, '').path()
	try:
		with open(full_path, 'rb'):
			pass
	except FileNotFoundError:
		return Response('File not found.', 404)

	mime = mimetypes.guess_type(path)
	file_size = os.stat(full_path).st_size

	range_header = request.headers.get('Range')

	resp = Response(
		file_stream(full_path, range_header),
		200,
		mimetype=mime[0],
		content_type=mime[0],
		direct_passthrough=True,
		headers={
			'Accept-Ranges': 'bytes',
			'Content-Length': str(file_size),
		}
	)
	return resp


def download(path: str) -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	return stream(path)


def preview(path: str) -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	full_path = blob.BlobPreview(files.sanitize_path(path), '').path()
	return files.read_file_data(full_path)


def upload() -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	if not perms.satisfies(('edit',)):
		return Response('You are not allowed to perform this action.', 403)

	auto_unzip = request.form['unzip'] == 'true'
	hidden = request.form['hidden'] == 'true'
	ephemeral = request.form['ephemeral'] == 'true'
	tag_list = json.loads(request.form['tags'])
	uploaded_blobs = blob.save_blob_data(
		request.files['file'],
		auto_unzip,
		tag_list,
		hidden,
		ephemeral
	)

	return jsonify(uploaded_blobs)
