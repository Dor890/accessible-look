import os
import json

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableDict

from query_manager import query_place, query_final_result
from utils import PDF

db = SQLAlchemy()
migrate = Migrate()

SUPPORTED_PLACES_PATH = os.path.join('static', 'supported_places.json')
with open(SUPPORTED_PLACES_PATH, 'r', encoding='utf-8') as file:
    supported_places = json.load(file)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20))
    main_image = db.Column(db.String)
    places = db.Column(MutableDict.as_mutable(JSON), default={})
    pdf_report_path = db.Column(db.String, default='')
    final_result = db.Column(db.String, default='')

    def add_place(self, place, images, result):
        if place not in self.places:
            self.places[place] = {'images': [], 'result': result, 'summary': ''}
        self.places[place]['images'].extend(images)
        self.places[place]['summary'] = list(self.places[place]['result'].values())[-1]
        db.session.commit()

    def produce_final_result(self):
        places_with_photos = [place for place in supported_places if place in self.places]

        if len(places_with_photos) == len(supported_places):
            results = {place: self.places[place]['result'] for place in supported_places}

            # Generate final result using the query_final_result function
            final_result = query_final_result(results)

            # Save the final result
            self.final_result = final_result

            # Generate PDF report
            reports_path = os.path.join('static', 'reports')
            if not os.path.exists(reports_path):
                os.makedirs(reports_path)
            report_file_path = os.path.join(reports_path, f"user_{self.id}_report.pdf")

            # Create PDF instance
            pdf = PDF()

            for line in final_result.split('\n'):
                # Detect headers and regular text
                if line.startswith("###"):
                    hebrew_text = line[4:]
                    pdf.write_hebrew(hebrew_text, 'Title')
                elif line.startswith("- **"):
                    hebrew_text = line[4:].replace("**", "")
                    pdf.write_hebrew(hebrew_text, 'Subtitle')
                else:
                    hebrew_text = line
                    pdf.write_hebrew(hebrew_text, 'Normal')

            # Build the PDF
            pdf.output(report_file_path)

            # Save PDF reports_path in the user's data
            self.pdf_report_path = report_file_path
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
    filepath = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place = db.Column(db.String(255))