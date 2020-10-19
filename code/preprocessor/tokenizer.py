from .utils import abbreviations
from hashlib import md5
import re

class Tokenizer:

    def __init__(self, abbreviations_filepath):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviation_dictionary = {" " + abbreviation:md5(abbreviation.encode()).hexdigest() for abbreviation in abbreviations(abbreviations_filepath)}

    def tokenize(self, sentence):
        """
        Tokenises a string by splitting it at the spaces (one or more).
        ".", "!", "?", ", ", ": ", ";", "(", ")","[", "]", "{", "}", "/", "\\" and " - " are first isolated
        from any preceding or following characters by insertion of a space before and after them.
        
        Args:
            sentence: A string representation of a sentence.

        Returns:
            A list of strings representing the sentence, including punctuation.
        """
        encountered_abbreviations = {}
        for abbreviation in self.abbreviation_dictionary:
            if abbreviation in sentence:
                hashed_abbreviation = " " + self.abbreviation_dictionary[abbreviation]
                sentence = sentence.replace(abbreviation, hashed_abbreviation)
                encountered_abbreviations[hashed_abbreviation] = abbreviation
        for mark in [".","!","?",", ",": ",";", "(", ")","[","]","{","}","/","\\", "-"]:
            sentence = sentence.replace(mark, " " + mark + " ")
        for encountered_abbreviation in encountered_abbreviations:
            sentence = sentence.replace(encountered_abbreviation, encountered_abbreviations[encountered_abbreviation])
        split_sentence = re.split(" +", sentence.strip())

        return split_sentence
