"""application.types"""

from .blob_storage import *
import json


def wrapped_default(self, obj):
    """
    Serializes an object to a dictionary representation.

    If the object has a `__dict__` attribute, it returns a dictionary containing
    the class name under the key `__typename` and the object's dictionary items.
    Otherwise, it returns the object itself.

    Args:
        obj: The object to be serialized.

    Returns:
        dict: A dictionary representation of the object if it has a `__dict__` attribute.
        Otherwise, returns the object itself.
    """
    return {'__typename': obj.__class__.__name__, **obj.__dict__} if getattr(obj, '__dict__') else obj


## Monkey patch the default method of the JSONEncoder class to use the wrapped_default function.
## This will allow us to serialize objects to JSON without having to write custom serialization functions for each object.
json.JSONEncoder.default = wrapped_default
