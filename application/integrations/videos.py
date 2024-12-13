from imageio.v3 import imread, imwrite


def extensions() -> list:
	return ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg']


def create_preview_from_first_frame(video_path: str, output_image: str) -> None:
	first_frame = imread(video_path, index=0)
	imwrite(output_image, first_frame)
