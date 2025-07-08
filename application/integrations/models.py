"""application.integrations.models"""

import trimesh


def extensions():
	"""
	Returns a list of file extensions commonly used for 3D models.

	Returns:
		list: A list of strings, each representing a file extension for 3D model files.
	"""
	return [
		'3ds', '.3mf', '.amf', '.ase', '.rvm', '.dae', '.drc',
		'.dxf', '.fbx', '.gltf', '.obj', '.ma', '.mb', '.ply',
		'.jt', '.stl', '.u3d', '.usd', '.usdz', '.x', '.x3d',
		'.xgl', '.zpr'
	]


def to_glb(input_filename: str, output_filename: str) -> None:
	"""
	Converts a 3D mesh file to GLB format.

	Args:
		input_filename (str): The path to the input 3D mesh file.
		output_filename (str): The path where the output GLB file will be saved.

	Returns:
		None

	Raises:
		ValueError: If the input file cannot be loaded as a 3D mesh.
	"""
	mesh = trimesh.load(input_filename, force='mesh')

	if not isinstance(mesh, trimesh.Trimesh):
		print(f'MESH ERROR: Cannot load file as 3D mesh: {input_filename}')
		return

	mesh.export(output_filename, file_type='glb')
