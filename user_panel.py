import json
import query_manager

from utils import display_images_from_base64

QUERIES_JSON = 'db/queries.json'

with open(QUERIES_JSON, 'r') as file:
    queries_dict = json.load(file)


class User:
    def __init__(self, username, password):
        self._username = username
        self.__password = password
        self.places = {}
        self.final_result = ''

    def add_place(self, place, images, response):
        self.places[place] = {}
        self.places[place]['images'] = images
        self.places[place]['response'] = response

    def validate_password(self, password):
        return self.__password == password

    def produce_final_result(self):
        pass

    def get_username(self):
        return self._username

    def display_images(self):
        for place in self.places:
            display_images_from_base64(place['images'])
            print(f"Condition: {place.response}")

    def query_new_place(self, place):
        query = queries_dict.get(place)
        if query is None:
            print("Place isn't in the supported options.")
        base64_images, result = query_manager.query_place(self, place, query)
        # Update the DB with images & results
        self.add_place(place, base64_images, result)

    def action_center(self):
        while True:
            print("What would you like to do?")
            print("1. Upload photos")
            print("2. Display my images")
            print("3. Print final result")
            print("4. Save and Quit")

            action = input("Choose your action: ")
            if action == '1':
                print(f"Supported places: {queries_dict.keys()}")
                place = input("Choose your place: ")
                self.query_new_place(place)

            if action == '2':
                self.display_images()

            if action == '3':
                self.produce_final_result()
                print(self.final_result)

            if action == '4':
                # Save and quit
                pass
