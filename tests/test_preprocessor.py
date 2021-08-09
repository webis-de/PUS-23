from code.preprocessor.preprocessor import Preprocessor
from os.path import sep
import unittest

class TestPreprocessor(unittest.TestCase):

    def test_preprocessor(self):
        TEXT = "This is a text with an abbr., i.e. common shortened words and phrases. It also contains a filter word (it's this one)!"
        preprocessor = Preprocessor("en", ["filter word"])
        
        preprocessed_text = preprocessor.preprocess(TEXT, lower=True, stopping=False, sentenize=False, tokenize=False)[0]
        self.assertEqual("this is a text with an abbr., i.e. common shortened words and phrases. it also contains a filter word (it is this one)!",
                         preprocessed_text)

        preprocessed_text = preprocessor.preprocess(TEXT, lower=False, stopping=True, sentenize=False, tokenize=False)[0]
        self.assertEqual("This is a text with an abbr., i.e. common shortened words and phrases. It also contains a filter word (it is this one)!",
                         preprocessed_text)

        preprocessed_text = preprocessor.preprocess(TEXT, lower=False, stopping=False, sentenize=True, tokenize=False)
        self.assertEqual(["This is a text with an abbr., i.e. common shortened words and phrases.", "It also contains a filter word (it is this one)!"],
                         preprocessed_text)

        preprocessed_text = preprocessor.preprocess(TEXT, lower=True, stopping=False, sentenize=True, tokenize=True)
        self.assertEqual([['this', 'is', 'a', 'text', 'with', 'an', 'abbr.', ',', 'i.e.', 'common', 'shortened', 'words', 'and', 'phrases', '.'],
                          ['it', 'also', 'contains', 'a', 'filter word', '(', 'it', 'is', 'this', 'one', ")", '!']],
                         preprocessed_text)
        
        preprocessed_text = preprocessor.preprocess(TEXT, lower=False, stopping=False, sentenize=False, tokenize=True)[0]
        self.assertEqual(len(preprocessed_text), 27)
        self.assertIn("abbr.", preprocessed_text)
        self.assertIn("i.e.", preprocessed_text)
        self.assertIn("filter word", preprocessed_text)
        
        preprocessed_text = preprocessor.preprocess(TEXT, lower=False, stopping=True, sentenize=False, tokenize=True)[0]
        self.assertEqual(len(preprocessed_text), 11)
        self.assertIn("abbr.", preprocessed_text)
        self.assertIn("i.e.", preprocessed_text)
        self.assertIn("filter word", preprocessed_text)
        self.assertNotIn("is", preprocessed_text)
        self.assertNotIn("a", preprocessed_text)
        self.assertNotIn("and", preprocessed_text)
        self.assertNotIn("s", preprocessed_text)
    
if __name__ == "__main__":
    unittest.main()
