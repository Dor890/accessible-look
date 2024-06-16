import os
import re
import json

from bidi.algorithm import get_display
import arabic_reshaper
from fpdf import FPDF


def get_queries_dict():
    queries_path = os.path.join('static', 'queries.json')

    with open(queries_path, 'r', encoding='utf-8') as file:
        queries_dict = json.load(file)

    return queries_dict


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
