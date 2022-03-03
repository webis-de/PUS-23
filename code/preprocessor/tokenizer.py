from .utils import abbreviations
from hashlib import md5
import re

class Tokenizer:

    def __init__(self, abbreviations_filepath, filterwords = []):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviation_dictionary = {abbreviation:md5(abbreviation.encode()).hexdigest()
                                        for abbreviation in abbreviations(abbreviations_filepath)}
        self.inverted_abbreviation_dictionary = {v:k for k,v in self.abbreviation_dictionary.items()}
        self.filterwords = filterwords

    def tokenize(self, string):
        """
        Tokenises a string by splitting it at the spaces (one or more).
        ".", "!", "?", ", ", ": ", ";", "(", ")","[", "]", "{", "}", "/", "\\", "|" and " - " are first isolated
        from any preceding or following characters by insertion of a space before and after them.
        
        Args:
            string: The string to tokenize.

        Returns:
            A list of tokens extracted from the string, including punctuation.
        """
        masked_filterwords = {}
        for filterword in self.filterwords:
            for filterword_to_mask in re.findall(filterword, string):
                masked_filterword = md5(filterword_to_mask.encode()).hexdigest()
                masked_filterwords[masked_filterword] = filterword_to_mask
                string = string.replace(filterword_to_mask, " " + masked_filterword)
                
        for abbreviation in self.abbreviation_dictionary:
            for abbreviation_to_mask in re.findall("[^a-zA-Z]" + abbreviation.replace(".","\."), string):
                string = string.replace(abbreviation_to_mask, abbreviation_to_mask[0] + self.abbreviation_dictionary[abbreviation_to_mask[1:]])

        for mark in [".","!","?",", ",": ",";", "(", ")","[","]","{","}","/","\\","'","\"", "|"]:
            string = string.replace(mark, " " + mark + " ")

        tokens = re.split("[ \n]+", string.strip(), flags=re.M)

        return [self.inverted_abbreviation_dictionary.get(masked_filterwords.get(token, token),
                                                           masked_filterwords.get(token, token))
                .strip()
                for token in tokens]
