import os
import json

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from query_manager import query_place, query_final_result

db = SQLAlchemy()
migrate = Migrate()

SUPPORTED_PLACES_PATH = os.path.join('static', 'supported_places.json')
with open(SUPPORTED_PLACES_PATH, 'r', encoding='utf-8') as file:
    supported_places = json.load(file)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    places = db.Column(db.JSON, default={})
    final_result = db.Column(db.String, default='')

    def add_place(self, place, images, result):
        if place not in self.places:
            self.places[place] = {'images': [], 'result': result}
        self.places[place]['images'].extend(images)
        db.session.commit()

    def produce_final_result(self):
        # Check if the user has uploaded photos for all supported places
        places_with_photos = [place for place in supported_places if place in self.places]

        # Check if the user has uploaded photos for all supported places
        if len(places_with_photos) == len(supported_places):
            # Gather the results for each place
            results = {place: self.places[place]['response'] for place in supported_places}

            # Send all results to the query_final_result function
            final_result = query_final_result(results)

            # Update the user's final result
            self.final_result = final_result

            # Commit changes to the database
            db.session.commit()

            return final_result
        else:
            return None

    def query_and_update_place(self, place):
        # Query the place
        base64_images, result = query_place(self, place)
        # Add the queried place to user data
        self.add_place(place, base64_images, result)
        # Commit changes to the database
        db.session.commit()

    def can_create_review(self):
        # Check if the user has uploaded images for all places
        places_uploaded = set(self.places.keys())

        return set(supported_places).issubset(places_uploaded)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary)
    filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place = db.Column(db.String(255))
