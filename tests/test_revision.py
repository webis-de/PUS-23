from code.article.revision.revision import Revision
import unittest
from json import loads

class TestRevision(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Revision 51 (index 50) of CRISPR
        # https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=369962884
        with open("tests/revisions/revision1.json") as revision_file:
            cls.revision1 = Revision(**loads(revision_file.readline()))
        # Revision 2092 (index 2091) of CRISPR
        # https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=1009355338
        with open("tests/revisions/revision2.json") as revision_file:
            cls.revision2 = Revision(**loads(revision_file.readline()))

    def test_metadata_revision1(self):
        self.assertEqual(369962884, self.revision1.revid)
        self.assertEqual(368675436, self.revision1.parentid)
        self.assertEqual("https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=369962884", self.revision1.url)
        self.assertEqual("152.3.197.128", self.revision1.user)
        self.assertEqual(0, self.revision1.userid)
        self.assertEqual("2010-06-24T19:24:03Z", self.revision1.timestamp.timestamp_string())
        self.assertEqual(6000, self.revision1.size)
        self.assertEqual("", self.revision1.comment)
        self.assertEqual("", self.revision1.minor)
        self.assertEqual(50, self.revision1.index)

    def test_metadata_revision2(self):
        self.assertEqual(1009355338, self.revision2.revid)
        self.assertEqual(1008819779, self.revision2.parentid)
        self.assertEqual("https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=1009355338", self.revision2.url)
        self.assertEqual("24.84.219.95", self.revision2.user)
        self.assertEqual(0, self.revision2.userid)
        self.assertEqual("2021-02-28T03:55:25Z", self.revision2.timestamp.timestamp_string())
        self.assertEqual(131170, self.revision2.size)
        self.assertEqual("grammar", self.revision2.comment)
        self.assertEqual("", self.revision2.minor)
        self.assertEqual(2091, self.revision2.index)

    def test_get_references(self):
        # 1 deprecated reference + 7 references
        self.assertEqual(8, len(self.revision1.get_references()))
        # 2 elements in 'Notes' (due to <cite> tag) + 190 elements in "References'
        self.assertEqual(192, len(self.revision2.get_references())) #includes Notes due to cite tag

    def test_get_further_reading(self):
        # no 'Further Reading' section
        self.assertEqual(0, len(self.revision1.get_further_reading()))
        # 17 elements in 'Further Reading' section
        self.assertEqual(17, len(self.revision2.get_further_reading()))

if __name__ == "__main__":
    unittest.main()



