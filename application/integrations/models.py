__ALL__ = ['to_glb', 'extensions']

from pathlib import Path
from . import exceptions
import aspose.threed as a3d

def extensions():
	return ['3ds', '.3mf', '.amf', '.ase', '.rvm', '.dae', '.drc', '.dxf', '.fbx', '.gltf', '.obj', '.ma', '.mb', '.ply', '.jt', '.stl', '.u3d', '.usd', '.usdz', '.x']

def to_glb(input_filename: str, output_filename: str) -> None:
	scene = a3d.Scene.from_file(input_filename)
	scene.save(output_filename)
