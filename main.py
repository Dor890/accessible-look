import os

from users import User, Users
from chat_api import ask_openai_with_image
from utils import convert_images_in_directory_to_base64 as photos_to_base64


def door_photos(user):
    door_photos_path = f'/db/{user.username}'
    # Validate the path
    if os.path.exists(door_photos_path) and os.path.isdir(door_photos_path):
        print(f"Door photos have been provided. Proceeding...")
        query = ''
        door_base64_photos = photos_to_base64(door_photos_path)
        result = ask_openai_with_image(query, door_base64_photos)
        user.add_place('door', door_base64_photos, result)
        return result
    else:
        print(f"{user} has not provided any door photos yet.")


def main():
    users = Users()
    users.load_users()

    print("Welcome to Accessible-Look!")

    print("Please log in:")
    while True:
        username = input("username: ")
        password = input("password: ")
        user = users.login(username, password)
        if user:
            break

    response = door_photos(user)
    print(response)


if __name__ == "__main__":
    main()