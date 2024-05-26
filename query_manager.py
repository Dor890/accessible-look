import os
import json

from chat_api import ask_chat_gpt_with_images
from utils import convert_images_in_directory_to_base64 as photos_to_base64

QUERIES_JSON = '/db/queries.json'


def query_place(user, place):
    images_path = f'/db/{user.username}/{place}'

    # Receive Images
    images = receive_images(images_path)

    # Convert images to Base64
    base64_photos = photos_to_base64(images)

    # Load the specific query
    query = load_query(place)

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


def load_query(place):
    try:
        with open(QUERIES_JSON, 'r') as file:
            data = json.load(file)

        if place in data:
            return data[place]
        else:
            raise KeyError(f"Key '{place}' not found in the JSON file.")

    except Exception as e:
        print(f"An error occurred while loading the JSON file: {e}")
        raise
