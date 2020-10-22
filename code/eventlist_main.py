from entity.bibliography import Bibliography
from entity.accountlist import AccountList
from entity.eventlist import EventList

el = EventList("../data/CRISPR_events - events.csv",
               Bibliography("../data/tracing-innovations-lit.bib"),
               AccountList("../data/CRISPR_events - accounts.csv"))

##for event in el.events:
##    if event.sampled:
##        print(event)
##        print("-"*50)

from pprint import pprint
pprint(el.events[2].json())
