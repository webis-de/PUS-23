from code.timeline.event import Event
from os.path import sep

import unittest

class MockedAccountList:

    def __init__(self):

        self.accounts = {1:"1", 2:"2", 3:"3", 4:"4", 5:"5"}

class MockedBibliography:

    def __init__(self):

        self.bibentries = {}

    def get_bibentries(self, bib_keys):
        return {bib_key:self.bibentries.get(bib_key) for bib_key in bib_keys if self.bibentries.get(bib_key)}
    
class TestEvent(unittest.TestCase):

    def test_equalling(self):

        accountList = MockedAccountList()
        bibliography = MockedBibliography()
        
        event1 = Event({"event_id": "1",
                        "event_year": "2020",
                        "event_month": "1",
                        "event_day":"1",
                        "account_id": "1",
                        "accountlist": accountList,
                        "bibliography": bibliography,
                        "sampled": "1",
                        "event_text": "eventtext1",
                        "type": "type1",
                        "subtype": "subtype1",
                        "bib_keys": "",
                        "wos_keys": "",
                        "comment": "comment1",
                        "extracted_from":"extracted_from1"},
                       bibliography,
                       accountList)
        event1.bibentries = {"bibkey1":1}
        event2 = Event({"event_id": "2",
                        "event_year": "2020",
                        "event_month": "2",
                        "event_day": "2",
                        "account_id": "2",
                        "accountlist": accountList,
                        "bibliography": bibliography,
                        "sampled": "1",
                        "event_text": "eventtext2",
                        "type": "type2",
                        "subtype": "subtype2",
                        "bib_keys": "",
                        "wos_keys": "",
                        "comment": "comment2",
                        "extracted_from":"extracted_from2"},
                       bibliography,
                       accountList)
        event2.bibentries = {"bibkey2":2}       
        event3 = Event({"event_id": "1",
                        "event_year": "2020",
                        "event_month": "3",
                        "event_day": "3",
                        "account_id": "3",
                        "accountlist": accountList,
                        "bibliography": bibliography,
                        "sampled": "1",
                        "event_text": "eventtext3",
                        "type": "type3",
                        "subtype": "subtype3",
                        "bib_keys": "",
                        "wos_keys": "",
                        "comment": "comment3",
                        "extracted_from":"extracted_from3"},
                       bibliography,
                       accountList)
        event3.bibentries = {"bibkey3":3}
        
        event4 = Event({"event_id": "4",
                        "event_year": "2020",
                        "event_month": "4",
                        "event_day": "4",
                        "account_id": "4",
                        "accountlist": accountList,
                        "bibliography": bibliography,
                        "sampled": "1",
                        "event_text": "eventtext4",
                        "type": "type4",
                        "subtype": "subtype4",
                        "bib_keys": "",
                        "wos_keys": "",
                        "comment": "comment4",
                        "extracted_from":"extracted_from4"},
                       bibliography,
                       accountList,
                       ["bibentries.keys()"])
        event4.bibentries = {"bibkey4":"foo"}
        event5 = Event({"event_id": "5",
                        "event_year": "2020",
                        "event_month": "5",
                        "event_day": "5",
                        "account_id": "5",
                        "accountlist": accountList,
                        "bibliography": bibliography,
                        "sampled": "1",
                        "event_text": "eventtext5",
                        "type": "type5",
                        "subtype": "subtype5",
                        "bib_keys": "",
                        "wos_keys": "",
                        "comment": "comment5",
                        "extracted_from":"extracted_from5"},
                       bibliography,
                       accountList,
                       ["bibentries.keys()"])
        event5.bibentries = {"bibkey4":"bar"}

        events = [event1, event2]

        self.assertNotEqual(event1, event2)
        self.assertEqual(event1, event3)
        self.assertEqual(event4, event5)
        self.assertIn(event3, events)
        self.assertNotIn(event4, events)
    
if __name__ == "__main__":
    unittest.main()

