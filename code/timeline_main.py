from bibliography.bibliography import Bibliography
from timeline.accountlist import AccountList
from timeline.eventlist import EventList
from pprint import pprint

el = EventList("../data/CRISPR_events - events.csv",
               Bibliography("../data/tracing-innovations-lit.bib"),
               AccountList("../data/CRISPR_events - accounts.csv"))

if False:
    for event in el.events:
        if event.sampled and event.bib_keys: 
            print(event)
            print("-"*50)
else:
    print("="*50)
    print(el.events[124])
    print("="*50)
    pprint(el.events[124].json())
