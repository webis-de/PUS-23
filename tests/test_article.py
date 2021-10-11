from code.article.article import Article
import unittest

class TestRevision(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.article = Article("tests/data/6S_%2F_SsrS_RNA_en")

    def test_name(self):
        self.assertEqual(self.article.name, "6S / SsrS RNA")

    def test_get_revision_count(self):
        self.assertEqual(self.article.get_revision_count(), 54)

    def test_get_revision(self):
        self.assertEqual(self.article.get_revision(index=0, revid=None).revid, 131124859)
        self.assertEqual(self.article.get_revision(index=53, revid=None).revid, 997696733)
        self.assertEqual(self.article.get_revision(index=None, revid=131124859).index, 0)
        self.assertEqual(self.article.get_revision(index=None, revid=997696733).index, 53)

    def test_get_revisions(self):
        revisions = self.article.get_revisions(2,5)
        self.assertEqual(len(revisions), 4)
        self.assertEqual(revisions[0].revid, 134932548)
        self.assertEqual(revisions[-1].revid, 163316452)
        
