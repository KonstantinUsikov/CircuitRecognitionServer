import base64
import json
import os
from typing import List


def read_image(image_path: str) -> bytes:
    with open(image_path, 'rb') as image:
        return image.read()


def read_images(image_paths: List[str]) -> List[bytes]:
    images = []
    for path in image_paths:
        images.append(read_image(path))
    return images


def encode_images(images: List[bytes]) -> str:
    encoded_images = []
    for image in images:
        encoded_images.append(base64.b64encode(image).decode('utf-8'))
    return json.dumps(encoded_images)


def decode_images(images: str) -> List[bytes]:
    decoded_images = []
    for encoded_image in json.loads(images):
        decoded_images.append(base64.b64decode(encoded_image))
    return decoded_images

def encode_image(image: bytes) -> str:
    if isinstance(image, str):
        image = image.encode('utf-8')
    encoded_image = base64.b64encode(image).decode('utf-8')
    return encoded_image

def decode_image(image: str) -> bytes:
    return base64.b64decode(image)

def get_image_paths_from_folder(folder_path: str) -> List[str]:
    image_paths = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.svg'):
            image_paths.append(os.path.join(folder_path, file_name))
    return image_paths
