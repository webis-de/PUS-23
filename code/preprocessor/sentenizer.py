from .utils import abbreviations
from hashlib import md5
import re

class Sentenizer:

    def __init__(self, abbreviations_filepath):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviation_dictionary = {" " + abbreviation:md5(abbreviation.encode()).hexdigest() for abbreviation in abbreviations(abbreviations_filepath)}

    def sentenize(self, text):
        """
        Sentenizes a string by splitting it at the characters '.', '!' and '?'.
        
        Args:
            text: A string representation of a text.

        Returns:
            A list of strings representing all sentences in the text.
        """
        encountered_abbreviations = {}
        for abbreviation in self.abbreviation_dictionary:
            if abbreviation in text:
                hashed_abbreviation = " " + self.abbreviation_dictionary[abbreviation]
                text = text.replace(abbreviation, hashed_abbreviation)
                encountered_abbreviations[hashed_abbreviation] = abbreviation
        marks = []
        for character in text:
            if character in ['.', '!', '?']:
                marks.append(character)
        split_text = re.split("[\.!?]", text.strip())
        for i in range(len(split_text)):
            for encountered_abbreviation in encountered_abbreviations:
                split_text[i] = split_text[i].replace(encountered_abbreviation, encountered_abbreviations[encountered_abbreviation])
        return [split_text[i] + marks[i] if i < len(marks) else split_text[i] for i in range(len(split_text))]
