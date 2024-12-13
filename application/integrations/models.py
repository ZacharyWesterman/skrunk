__ALL__ = ['to_glb', 'extensions']

import trimesh


def extensions():
	return ['3ds', '.3mf', '.amf', '.ase', '.rvm', '.dae', '.drc', '.dxf', '.fbx', '.gltf', '.obj', '.ma', '.mb', '.ply', '.jt', '.stl', '.u3d', '.usd', '.usdz', '.x']


def to_glb(input_filename: str, output_filename: str) -> None:
	mesh = trimesh.load(input_filename, force='mesh')

	if not isinstance(mesh, trimesh.Trimesh):
		print(f'MESH ERROR: Cannot load file as 3D mesh: {input_filename}')
		return

	mesh.export(output_filename, file_type='glb')
