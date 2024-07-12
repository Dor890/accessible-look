import os
import re
import json
from datetime import datetime

from sqlalchemy import JSON
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict

from utils import PDF, encode_image
from query_manager import query_place, query_comment, query_final_result

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
    address = db.Column(db.String(30))
    main_image = db.Column(db.String)
    places = db.Column(MutableDict.as_mutable(JSON), default={})
    non_existing_places = db.Column(MutableDict.as_mutable(JSON), default={})
    pdf_report_path = db.Column(db.String, default='')
    final_result = db.Column(db.String, default='')

    def add_place(self, place, images, result):
        if place not in self.places:
            self.places[place] = {'images': [], 'result': result, 'summary': '', 'exists': True}
        self.places[place]['images'].extend(images)
        self.places[place]['summary'] = list(self.places[place]['result'].values())[-1]
        db.session.commit()

    def produce_final_result(self):
        places_with_photos = [place for place in supported_places if place in self.places and self.places[place]['images']]
        if len(places_with_photos) == len(supported_places) - len(self.non_existing_places):
            results = {place: self.places[place]['result'] for place in places_with_photos}
            final_result = query_final_result(results)
            self.final_result = final_result

            reports_path = os.path.join('static', 'reports')
            if not os.path.exists(reports_path):
                os.makedirs(reports_path)
            report_file_path = os.path.join(reports_path, f"user_{self.id}_report.pdf")

            pdf = PDF()
            pdf.cover_page(self)
            toc_items = []
            current_page = 1
            for line in final_result.split('\n'):
                if line.startswith("###"):
                    current_page += 1
                    title = line[4:]
                    toc_items.append({"title": title, "page": current_page if current_page > 2 else 3})
            pdf.table_of_contents(toc_items)
            pdf.add_page()
            for line in final_result.split('\n'):
                if line.startswith("###"):
                    hebrew_text = line[4:]
                    pdf.write_hebrew(hebrew_text, 'Title')
                    place_name = hebrew_text.strip()
                    if place_name in self.places:
                        pdf.add_base64_images(self.places[place_name]['images'], place_name, width=50, height=50)
                elif line.startswith("- **"):
                    hebrew_text = line[4:].replace("**", "")
                    pdf.write_hebrew(hebrew_text, 'Subtitle')
                elif re.match(r"^\d+\. \*\*", line):
                    hebrew_text = line.replace("**", "")
                    pdf.write_hebrew(hebrew_text, 'Normal')
                else:
                    hebrew_text = line
                    pdf.write_hebrew(hebrew_text, 'Normal')
            pdf.output(report_file_path)
            self.pdf_report_path = report_file_path
            db.session.commit()
            return final_result
        else:
            return None

    def query_and_update_place(self, place):
        if place in self.places and not self.places[place]['images']:
            self.places[place]['summary'] = 'המשתמש הצהיר כי המקום לא קיים בעסק.'

        else:
            base64_images, result = query_place(self, place)
            self.add_place(place, base64_images, result)
        db.session.commit()

    def reset_place(self, place):
        if place in self.places:
            del self.places[place]
            if place in self.non_existing_places:
                del self.non_existing_places[place]
            if self.final_result:
                self.final_result = ''
            db.session.commit()

    def can_create_review(self):
        places_uploaded = set(self.places.keys())
        places_existing = set(supported_places) - set(self.non_existing_places.keys())
        return places_existing.issubset(places_uploaded)

    def add_main_image(self, file_path):
        new_image = Image(filepath=file_path, user_id=self.id, place='main_image')
        db.session.add(new_image)
        encoded_img = encode_image(file_path)
        self.main_image = encoded_img
        db.session.commit()

    def query_and_update_comment(self, place, comment):
        response = query_comment(self.places[place]['result'], comment.image_data, comment.comment_text)
        comment.response = response
        db.session.commit()


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place = db.Column(db.String(255))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=True)  # Store images as LargeBinary
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    response = db.Column(db.Text)
