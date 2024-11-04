import json

#Monkey patch JSON serialization so that objects are JSON serializable
def wrapped_default(self, obj):
    return obj.__dict__ if getattr(obj, '__dict__') else obj
json.JSONEncoder.default = wrapped_default

#Then import database objects

from .blob_storage import *
