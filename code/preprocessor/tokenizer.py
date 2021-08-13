from .utils import abbreviations
from hashlib import md5
import re

class Tokenizer:

    def __init__(self, abbreviations_filepath, filterwords = []):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviations_dictionary = {abbreviation: md5(abbreviation.encode()).hexdigest()
                                         for abbreviation in abbreviations(abbreviations_filepath)}
        self.inverted_abbreviations_dictionary = {v:k for k,v in self.abbreviations_dictionary.items()}
        self.filterwords = filterwords

    def tokenize(self, string):
        """
        Tokenises a string by splitting it at the spaces (one or more).
        ".", "!", "?", ", ", ": ", ";", "(", ")","[", "]", "{", "}", "/", "\\" and " - " are first isolated
        from any preceding or following characters by insertion of a space before and after them.
        
        Args:
            string: The string to tokenize.

        Returns:
            A list of tokens extracted from the string, including punctuation.
        """
        for abbreviation in self.abbreviations_dictionary:
            if abbreviation in string:
                string = string.replace(abbreviation, self.abbreviations_dictionary[abbreviation])

        masked_filterwords = {}
        for filterword in self.filterwords:
            for filterword_to_mask in re.findall(filterword, string):
                masked_filterword = md5(filterword_to_mask.encode()).hexdigest()
                masked_filterwords[masked_filterword] = filterword_to_mask
                string = string.replace(filterword_to_mask, masked_filterword)

        for mark in [".","!","?",", ",": ",";", "(", ")","[","]","{","}","/","\\","'","\""]:
            string = string.replace(mark, " " + mark + " ")

        tokens = re.split("[ \n]+", string.strip(), flags=re.M)

        return [self.inverted_abbreviations_dictionary.get(masked_filterwords.get(token, token),
                                                           masked_filterwords.get(token, token))
                .strip()
                for token in tokens]
