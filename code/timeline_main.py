from bibliography.bibliography import Bibliography
from timeline.accountlist import AccountList
from timeline.eventlist import EventList

el = EventList("../data/CRISPR_events - events.csv",
               Bibliography("../data/tracing-innovations-lit.bib"),
               AccountList("../data/CRISPR_events - accounts.csv"))

for event in el.events:
    if event.sampled:
        print(event)
        print("-"*50)
