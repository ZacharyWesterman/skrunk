__ALL__ = ['to_glb', 'extensions']

from pathlib import Path
from . import exceptions
import aspose.threed as a3d

def extensions():
	return ['.abc', '.blend', '.dae', '.fbx', '.obj', '.ply', '.stl', '.usd', '.usda', '.usdc', '.wrl', '.x3d']

def to_glb(input_filename: str, output_filename: str) -> None:
	scene = a3d.Scene.from_file(input_filename)
	scene.save(output_filename)