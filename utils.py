import os
import io
import base64

from PIL import Image


def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format=img.format)
        img_byte = buffered.getvalue()
    img_base64 = base64.b64encode(img_byte).decode('utf-8')
    return img_base64


def convert_images_in_directory_to_base64(directory_path):
    base64_list = []
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
            file_path = os.path.join(directory_path, filename)
            img_base64 = image_to_base64(file_path)
            base64_list.append(img_base64)
    return base64_list
