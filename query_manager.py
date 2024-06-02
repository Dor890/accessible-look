import os
import json

from chat_api import ask_chat_gpt_with_images
from utils import convert_images_in_directory_to_base64 as photos_to_base64


def query_place(user, place,  query):
    images_path = f'/db/{user.username}/{place}'

    # Receive Images
    images = receive_images(images_path)

    # Convert images to Base64
    base64_photos = photos_to_base64(images)

    # Get ChatGPT results
    result = ask_chat_gpt_with_images(query, base64_photos)

    return base64_photos, result


def receive_images(images_path):
    # TODO: Make user upload photos
    if os.path.exists(images_path) and os.path.isdir(images_path):
        print(f"Photos have been provided. Proceeding...")
        return True
    else:
        print(f"You haven't provided any photos for this place yet.")  # Or invalid
        return False
