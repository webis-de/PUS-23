from .tokenizer import Tokenizer
from .sentenizer import Sentenizer
from .utils import stopwords, contractions
from re import sub
from os.path import exists

class Preprocessor:
    """
    Preprocessor module to wrap tokenization and sentenization.

    Attributes:
        tokenizer: The tokeniser this preprocessor uses.
        sentenizer: The sentenizer this preprocessor uses.
        stopwords: The list of stopwords this preprocessor uses.
    """
    def __init__(self, language, filterwords = []):

        prefix = "code/" if exists("code") else ""
        self.tokenizer = Tokenizer(prefix + "preprocessor/data/abbreviations_" + language + ".txt", filterwords)
        self.sentenizer = Sentenizer(prefix + "preprocessor/data/abbreviations_" + language + ".txt", filterwords)
        self.stopwords = stopwords(prefix + "preprocessor/data/stopwords_" + language + ".txt")
        self.contractions = contractions(prefix + "preprocessor/data/contractions_" + language + ".txt")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def preprocess(self, phrase, lower, stopping, sentenize, tokenize):
        """
        Main function for preprocessing a string.

        Args:
            phrase: The string to preprocess.
            lower: Lower characters if True.
            stopping: Remove stopwords if true.
            sentenize: Sentenize the string.
            tokenize: Tokenize the sentences.

        Returns:
            A list containing each sentence, as a list if tokenized.
            Returns the sting as a one-item list if no preprocessing flags were applied.
        """
        phrase = self.clean(phrase)

        phrase = self.sentenizer.sentenize(phrase) if sentenize else [phrase]

        phrase = [[token for token in self.tokenizer.tokenize(sentence) if token and (not stopping or token not in self.stopwords)]
                  for sentence in phrase] if tokenize else phrase

        phrase = [[token.lower() for token in item] if type(item) == list else item.lower() for item in phrase] if lower else phrase
                
        return phrase

    def clean(self, phrase):
        """
        Remove double periods and quotation marks.
        Transform contracted forms.

        Args:
            phrase: The string to clean.

        Returns:
            A string with all quotation marks and full stop sequences removed
            and all contracted forms split into parts.
        """
        for contraction in self.contractions:
            phrase = phrase.replace(contraction[0], contraction[1])
        #eliminate quotation marks
        # ['"', '`', '«', '»', '´', '‘', '’', '‚', '‛', '“', '”', '„', '‟', '‹', '›']
        for character in [chr(int(c, 16)) for c in ["0022","0060","00AB","00BB","00B4",
                                                    "2018","2019","201A","201B","201C","201D","201E","201F",
                                                    "2039","203A"]]:
            phrase = phrase.replace(character, " ")

        #eliminate double and multiple full stops
        phrase = sub("(\.+ *){2,}", " ", phrase)
        return phrase

    def dehyphenate(self, phrase):
        """
        Replace hyphens with blanks.
        Does not remove hyphens if preceded by one letter only to retain terms like 'e-mail'.

        Args:
            phrase: The string to remove hyphens from.

        Returns:
            A string where hyphens like 'word-hyphenation' are removed: 'word hyphenation'.
        """
        return sub("([a-zA-Z]{2,2}|^)-", "\g<1> ", phrase)
