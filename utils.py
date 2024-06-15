import os
import io
import base64
import re

from PIL import Image
from io import BytesIO

from bidi.algorithm import get_display
import arabic_reshaper
from fpdf import FPDF


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


def display_images_from_base64(images_base64):
    for img_base64 in images_base64:
        img_data = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_data))
        img.show()


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font('David', '', 'fonts/DavidLibre-Regular.ttf', uni=True)
        self.set_font('David', '', 12)
        self.set_right_margin(10)
        self.set_left_margin(10)
        self.set_auto_page_break(auto=True, margin=15)

    def write_hebrew(self, text, style='Body'):
        if style == 'Title':
            self.set_font('David', '', 18)
        elif style == 'Subtitle':
            self.set_font('David', '', 14)
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

        # Reverse the lines for RTL text
        for i, line in enumerate(lines):
            words = line.split()
            words.reverse()
            lines[i] = ' '.join(words)
        # lines.reverse()

        return lines