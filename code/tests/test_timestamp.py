from article.revision.timestamp import Timestamp
import unittest

class TestTimestamp(unittest.TestCase):

    def test_timestamp(self):
        timestamp = Timestamp("2020-7-6T17:10:20Z")
        self.assertEqual(str(timestamp), ("{'datetime': datetime.datetime(2020, 7, 6, 17, 10, 20),\n"
                                          " 'day': 6,\n"
                                          " 'hour': 17,\n"
                                          " 'minute': 10,\n"
                                          " 'month': 7,\n"
                                          " 'second': 20,\n"
                                          " 'string': '2020-07-06 17:10:20',\n"
                                          " 'year': 2020}"))

if __name__ == "__main__":
    unittest.main()



