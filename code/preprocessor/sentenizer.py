from .utils import abbreviations
from hashlib import md5
import re

class Sentenizer:

    def __init__(self, abbreviations_filepath):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviation_dictionary = {}
        for abbreviation in abbreviations(abbreviations_filepath):
            self.abbreviation_dictionary[" " + abbreviation] = " " + md5(abbreviation.encode()).hexdigest()
            self.abbreviation_dictionary["(" + abbreviation] = "(" + md5(abbreviation.encode()).hexdigest()
        self.inverted_abbreviation_dictionary = {v:k for k,v in self.abbreviation_dictionary.items()}

    def sentenize(self, text):
        """
        Sentenizes a string by splitting it at the characters '.', '!' and '?'.
        
        Args:
            text: A string representation of a text.

        Returns:
            A list of strings representing all sentences in the text.
        """
        masked_abbreviations = set()
        for abbreviation in self.abbreviation_dictionary:
            if abbreviation in text:
                text = text.replace(abbreviation, self.abbreviation_dictionary[abbreviation])
                masked_abbreviations.add(self.abbreviation_dictionary[abbreviation])

        marks = [character for character in text if character in ['.', '!', '?']]

        split_text = [sentence for sentence in re.split("[\.!?]", text.strip()) if sentence != ""]

        def dehash_abbreviations(sentence):
            for masked_abbreviation in masked_abbreviations:
                sentence = sentence.replace(masked_abbreviation, self.inverted_abbreviation_dictionary[masked_abbreviation])
            return sentence
        split_text = [dehash_abbreviations(sentence) for sentence in split_text]
        
        return [split_text[i].strip() + marks[i] if i < len(marks) else split_text[i] for i in range(len(split_text))]
