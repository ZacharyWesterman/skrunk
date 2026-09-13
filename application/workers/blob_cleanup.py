"""Periodically scan for orphan blobs and clean them up."""

from application.db.blob import delete_blob, get_old_ephemeral_blobs


def blob_cleanup() -> None:
	"""
	Periodically scan for orphan blobs and clean them up.
	"""

	deleted_ct = 0
	for blob_id in get_old_ephemeral_blobs():
		delete_blob(str(blob_id))

	if deleted_ct:
		print(f'Deleted {deleted_ct} orphan (ephemeral) blob entries.', flush=True)
