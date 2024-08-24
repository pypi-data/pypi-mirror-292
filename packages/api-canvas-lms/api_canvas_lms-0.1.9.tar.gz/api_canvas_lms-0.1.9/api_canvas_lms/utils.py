""" 
Programa : Utils module for Canvas
Fecha Creacion : 07/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging

import re
import unicodedata

# Create a logger for this module
logger = logging.getLogger(__name__)

# Function to clean HTML tags from the text
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def remove_tilde(text):
    # Normalize the text to decompose characters into base characters and diacritics
    normalized_text = unicodedata.normalize('NFD', text)
    # Filter out the diacritic marks
    filtered_text = ''.join([char for char in normalized_text if not unicodedata.combining(char)])
    return filtered_text

# Function to find all numbers in a given text
def find_first_number(text):
    # This regex finds all occurrences of one or more digits
    matches = re.findall(r'\d+', text)
    numbers = [int(num) for num in matches]
    return  numbers[0]

def get_coursename_and_sections_from_raw_coursename(raw_coursename):

    logging.debug(raw_coursename)
    fields_coursename = raw_coursename.split(' - ')
    coursename = fields_coursename[0]
    logging.debug(coursename)

    sections = []
    for field in fields_coursename[1:]:
        _splits = field.split('-')
        if len(_splits)>1:
            section = _splits[0][-1]
            logging.debug(field)
            logging.debug(section)
            sections.append(section)
    
    return coursename, sections