from preprocessor.preprocessor import Preprocessor
from utility.logger import Logger
from os.path import sep

TEST_DIRECTORY = ".." + sep + "test"

def test_preprocessor(logger):
    logger.start("Testing preprocessor...")
    TEXT = "This is a text with an abbr., i.e. common shortened words and phrases. It also contains a filter word. (It's this one!)"
    preprocessor = Preprocessor("en", ["filter word"])
    preprocessed_text = preprocessor.preprocess(TEXT, lower=False, stopping=False, sentenize=False, tokenize=True)[0]
    assert len(preprocessed_text) == 28
    assert "abbr." in preprocessed_text
    assert "i.e." in preprocessed_text
    assert "filter word" in preprocessed_text
    preprocessed_text = preprocessor.preprocess(TEXT, lower=False, stopping=True, sentenize=False, tokenize=True)[0]
    assert len(preprocessed_text) == 11
    assert "abbr." in preprocessed_text
    assert "i.e." in preprocessed_text
    assert "filter word" in preprocessed_text
    assert "is" not in preprocessed_text
    assert "a" not in preprocessed_text
    assert "and" not in preprocessed_text
    assert "s" not in preprocessed_text
    logger.stop("Preprocessor test successful.", 1)

if __name__ == "__main__":     
    
    with Logger(TEST_DIRECTORY) as LOGGER:
        test_preprocessor(LOGGER)
