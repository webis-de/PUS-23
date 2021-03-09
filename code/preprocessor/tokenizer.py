from .utils import abbreviations
from hashlib import md5
import re

class Tokenizer:

    def __init__(self, abbreviations_filepath, filterwords = []):
        self.abbreviations_filepath = abbreviations_filepath
        self.abbreviations_and_filterwords = set([word.replace(".","\.") for word in abbreviations(abbreviations_filepath)]).union(set(filterwords))

    def tokenize(self, string):
        """
        Tokenises a string by splitting it at the spaces (one or more).
        ".", "!", "?", ", ", ": ", ";", "(", ")","[", "]", "{", "}", "/", "\\" and " - " are first isolated
        from any preceding or following characters by insertion of a space before and after them.
        
        Args:
            sentence: A string representation of a sentence.

        Returns:
            A list of strings representing the sentence, including punctuation.
        """
        strings_to_escape = {}
        for pattern in self.abbreviations_and_filterwords:
            for string_to_escape in re.findall(pattern, string):
                hashed_string_to_escape = md5(string_to_escape.encode()).hexdigest()
                string = string.replace(string_to_escape, hashed_string_to_escape)
                strings_to_escape[hashed_string_to_escape] = string_to_escape
        for mark in [".","!","?",", ",": ",";", "(", ")","[","]","{","}","/","\\","'","\""]:
            string = string.replace(mark, " " + mark + " ")

        split_string = re.split("[ \n]+", string.strip(), flags=re.M)

        for i in range(len(split_string)):
            for string_to_escape in strings_to_escape:
                split_string[i] = split_string[i].replace(string_to_escape, strings_to_escape[string_to_escape])

        return split_string
