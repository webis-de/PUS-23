from .utils import abbreviations
from hashlib import md5
import re

class Sentenizer:

    def __init__(self, abbreviations_filepath, filterwords = []):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviation_dictionary = {}
        self.abbreviation_dictionary = {abbreviation:md5(abbreviation.encode()).hexdigest()
                                        for abbreviation in abbreviations(abbreviations_filepath)}
        self.inverted_abbreviation_dictionary = {v:k for k,v in self.abbreviation_dictionary.items()}
        self.filterwords = filterwords

    def sentenize(self, text):
        """
        Sentenizes a string by splitting it at the characters '.', '!' and '?'.
        
        Args:
            text: A string representation of a text.

        Returns:
            A list of strings representing all sentences in the text.
        """
        masked_filterwords = {}
        for filterword in self.filterwords:
            for filterword_to_mask in re.findall(filterword, text):
                masked_filterword = md5(filterword_to_mask.encode()).hexdigest()
                masked_filterwords[masked_filterword] = filterword_to_mask
                text = text.replace(filterword_to_mask, masked_filterword)
                
        masked_abbreviations = set()
        for abbreviation in self.abbreviation_dictionary:
            for abbreviation_to_mask in re.findall("[^a-zA-Z]" + abbreviation.replace(".","\."), text):
                masked_abbreviation = self.abbreviation_dictionary[abbreviation_to_mask[1:]]
                text = text.replace(abbreviation_to_mask, abbreviation_to_mask[0] + masked_abbreviation)
                masked_abbreviations.add(masked_abbreviation)

        marks = [character for character in text if character in ['.', '!', '?']]

        split_text = [sentence for sentence in re.split("[\.!?]", text.strip()) if sentence != ""]

        def demask(sentence):
            for masked_abbreviation in masked_abbreviations:
                sentence = sentence.replace(masked_abbreviation, self.inverted_abbreviation_dictionary[masked_abbreviation])
            for masked_filterword in masked_filterwords:
                sentence = sentence.replace(masked_filterword, masked_filterwords[masked_filterword])
            return sentence
        split_text = [demask(sentence) for sentence in split_text]
        
        return [split_text[i].strip() + marks[i] if i < len(marks) else split_text[i] for i in range(len(split_text))]
