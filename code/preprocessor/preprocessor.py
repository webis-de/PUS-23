from .tokenizer import Tokenizer
from .sentenizer import Sentenizer
from .utils import stopwords
from re import sub

class Preprocessor:
    """
    Preprocessor module to wrap tokenization and sentenization.

    Attributes:
        tokenizer: The tokeniser this preprocessor uses.
        sentenizer: The sentenizer this preprocessor uses.
        stopwords: The list of stopwords this preprocessor uses.
    """
    def __init__(self, language, filterwords = []):

        self.tokenizer = Tokenizer("preprocessor/data/abbreviations_" + language + ".txt", filterwords)
        self.sentenizer = Sentenizer("preprocessor/data/abbreviations_" + language + ".txt")
        self.stopwords = stopwords("preprocessor/data/stopwords_" + language + ".txt")

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
            Returns the sting of no preprocessing flags were applied.
        """
        if lower:
            phrase = phrase.lower()

        phrase = self.clean(phrase)

        if sentenize:
            phrase = self.sentenizer.sentenize(phrase)
        else:
            phrase = [phrase]

        if tokenize:
            if stopping:
                phrase = [[token for token in self.tokenizer.tokenize(sentence) if token not in self.stopwords] for sentence in phrase]
            else:
                phrase = [[token for token in self.tokenizer.tokenize(sentence)] for sentence in phrase]

        return phrase

    def clean(self, phrase):
        """
        Remove double periods and quotation marks.

        Args:
            phrase: The string to clean.

        Returns:
            A string with all quotation marks and full stop sequences removed.
        """
        #remove leading line number
        phrase = sub("^\d*\t", "", phrase)
        #remove value at end of line (deu_news_2012_1M-sentences.txt)
        phrase = sub("\t\d*\.\d*", "", phrase)
        #eliminate quotation marks
        phrase = phrase.replace("”", " ").replace("“", " ")
        phrase = phrase.replace("'"," ").replace("'"," ")
        phrase = phrase.replace("\""," ")
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
        
if __name__ == "__main__":
    text = "Das ist ein deutscher Text, der Kommas ... und Abkürzungen enthält. " + \
           "Darunter finden sich z.B. einige gängige Abkürzungen, aber auch einige andere seltenere Sachen " + \
           "wie i.A. für 'im Auftrag'."
    with Preprocessor(stopwords_filepath="utility/data/stopwords_de.txt.txt", abbreviations_filepath="utility/data/abbreviations_de.txt") as pp:
        for lower in [False, True]:
            for stopping in [False, True]:
                for sentenize in [False, True]:
                    for tokenize in [False, True]:
                        print(", ".join([item for item in ["lower" * lower, "stopping" * stopping, "sentenize" * sentenize, "tokenize" * tokenize] if item]))
                        print(pp.preprocess(text, lower, stopping, sentenize, tokenize))
                        print("="*30)

        print(sum([len(sentence) for sentence in pp.preprocess(text, lower=True, stopping=False, tokenize=True, sentenize=False)]))
        print(sum([len(sentence) for sentence in pp.preprocess(text, lower=True, stopping=False, tokenize=True, sentenize=True)]))
        print("="*30)        
        print(sum([len(sentence) for sentence in pp.preprocess(text, lower=True, stopping=True, sentenize=False, tokenize=True)]))
        print(sum([len(sentence) for sentence in pp.preprocess(text, lower=True, stopping=True, sentenize=True, tokenize=True)]))
        print("="*30)
