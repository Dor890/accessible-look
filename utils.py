import os
import re
import json
import base64
from datetime import datetime
from PIL import Image
import io

from bidi.algorithm import get_display
import arabic_reshaper
from fpdf import FPDF


def get_queries_dict():
    queries_path = os.path.join('static', 'queries.json')

    with open(queries_path, 'r', encoding='utf-8') as file:
        queries_dict = json.load(file)

    return queries_dict


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('David', '', 'fonts/DavidLibre-Regular.ttf', uni=True)
        self.add_font('David', 'B', 'fonts/DavidLibre-Bold.ttf', uni=True)
        self.set_font('David', '', 12)
        self.set_right_margin(15)
        self.set_left_margin(15)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('David', 'B', 12)
        self.image('static/images/logo-transparent.png', 10, 8, 45)
        self.cell(0, 10, '', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('David', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def cover_page(self, user):
        self.add_page()
        self.set_font('David', 'B', 24)
        title = 'תושיגנ חוד'
        business_name = f'Business Name: {user.name[::-1]}'
        business_id = f'Business ID: {user.id}'
        date = f'Date: {datetime.now().strftime("%d-%m-%Y")}'

        # Calculate vertical position for centering
        cover_text_height = 60  # Estimated height of the cover text block
        y_start = (self.h - cover_text_height) / 2

        self.set_y(y_start)
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(20)
        self.set_font('David', '', 16)
        self.cell(0, 10, business_name, 0, 1, 'C')
        self.cell(0, 10, business_id, 0, 1, 'C')
        self.cell(0, 10, date, 0, 1, 'C')
        self.ln(20)

    def table_of_contents(self, toc_items):
        self.add_page()
        self.set_font('David', 'B', 16)
        self.cell(0, 10, 'םיניינע ןכות', 0, 1, 'R')
        self.ln(10)
        self.set_font('David', '', 12)
        for item in toc_items:
            self.cell(0, 10, f'{item["page"]} ............................. {item["title"][::-1]}', 0, 1, 'R')
        self.ln(20)

    def add_base64_images(self, base64_images, place_name, width, height, tmp_dir='tmp_images'):
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        page_width = self.w
        margin_right = 15
        x_offset = page_width - margin_right - (width * len(base64_images)) - (5 * (len(base64_images) - 1))

        for idx, base64_image in enumerate(base64_images):
            image_data = base64.b64decode(base64_image)
            image_path = os.path.join(tmp_dir, f'temp_image_{place_name}_{idx}.png')
            image = Image.open(io.BytesIO(image_data))
            image.save(image_path, format='PNG')
            self.image(image_path, x=x_offset, y=self.get_y(), w=width, h=height)
            x_offset += width + 5
            os.remove(image_path)

        self.ln(height + 5)

    def write_hebrew(self, text, style='Body'):
        if style == 'Title':
            self.set_font('David', 'B', 18)
        elif style == 'Subtitle':
            self.set_font('David', 'B', 14)
        else:
            self.set_font('David', '', 12)

        paragraphs = text.split("\n")
        for paragraph in paragraphs:
            if paragraph.strip():
                reshaped_text = arabic_reshaper.reshape(paragraph)
                bidi_text = get_display(reshaped_text)
                self.write_hebrew_paragraph(bidi_text)
                self.ln(5)

    def write_hebrew_paragraph(self, text):
        page_width = self.w - self.r_margin - self.l_margin
        lines = self.split_text_to_lines(text, page_width)
        for line in lines:
            self.cell(0, 10, line, ln=True, align='R')

    def split_text_to_lines(self, text, max_width):
        words = re.split(r'(\s+)', text)
        words.reverse()
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + word if current_line else word
            if self.get_string_width(test_line) <= max_width:
                current_line = test_line
            else:
                if not current_line.strip():
                    lines.append(word.strip())
                else:
                    lines.append(current_line.strip())
                    current_line = word.strip()

        if current_line.strip():
            lines.append(current_line.strip())

        for i, line in enumerate(lines):
            words = line.split()
            words.reverse()
            lines[i] = ' '.join(words)
        return lines
