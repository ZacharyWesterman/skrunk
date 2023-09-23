from flask import jsonify, request, Response
import mimetypes
import os, re, json
from . import auth, files
from application.db import blob

application = None

def get_chunk(full_path: str, byte1: int, byte2: int) -> tuple:
	file_size = os.stat(full_path).st_size
	start = 0

	if byte1 < file_size:
		start = byte1
	if byte2:
		length = byte2 + 1 - byte1
	else:
		length = file_size - start

	length = min(length, 1024*1024*5) #Max chunk size is 5MiB

	with open(full_path, 'rb') as fp:
		fp.seek(start)
		chunk = fp.read(length)

	return chunk, start, length, file_size

def stream(path: str) -> Response:
	# if not auth.authorized():
	# 	return '', 403

	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	path = files.sanitize_path(path)

	range_header = request.headers.get('Range')
	byte1, byte2 = 0, None
	if range_header:
		match = re.search(r'(\d+)-(\d*)', range_header)
		groups = match.groups()

		if groups[0]:
			byte1 = int(groups[0])
		if groups[1]:
			byte2 = int(groups[1])

	full_path = blob.BlobStorage(path).path()
	try:
		chunk, start, length, file_size = get_chunk(full_path, byte1, byte2)
		mime = mimetypes.guess_type(path)

		resp = Response(chunk, 206, mimetype=mime[0], content_type=mime[0], direct_passthrough=True)
		resp.headers.add('Content-Range', f'bytes {start}-{start+length-1}/{file_size}')
		return resp
	except FileNotFoundError:
		return Response('File not found.', 404)

def download(path: str) -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	full_path = blob.BlobStorage(files.sanitize_path(path)).path()
	return files.read_file_data(full_path)

def preview(path: str) -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	full_path = blob.BlobPreview(files.sanitize_path(path)).path()
	return files.read_file_data(full_path)

def upload() -> Response:
	if not auth.authorized():
		return Response('Access denied.', 403)

	if application.blob_path is None:
		return Response('No blob data path specified in server setup.', 404)

	auto_unzip = request.form['unzip'] == 'true'
	tag_list = json.loads(request.form['tags'])
	uploaded_blobs = blob.save_blob_data(request.files['file'], auto_unzip, tag_list)

	return jsonify(uploaded_blobs)
