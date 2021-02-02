from os.path import basename, dirname, sep
from json import load, dumps
from path import json_path

verbatim_methods = ["titles",
                    "dois",
                    "pmids"]

relaxed_methods = ["ned <= 0.2",
                   "ned <= 0.3",
                   "ned <= 0.4",
                   "ned_and_ratio",
                   "ned_and_jaccard",
                   "ned_and_skat"
                   ]

with open(json_path) as file:
    events = load(file)

reduced_events = []

for event in events:
    methods = {}
    methods.update({k:v for k,v in event["first_mentioned"]["verbatim"].items() if v})
    methods.update({k:v for k,v in event["first_mentioned"]["relaxed"].items() if v})

    for method,occurrence in sorted(methods.items(), key = lambda item: item[1]["index"]):
        if method in verbatim_methods:
            occurrence["method"] = method
            event["first_mentioned"] = occurrence
            reduced_events.append(event)
            break
        else:
            bibkey = list(event["bibentries"].keys())[0]
            title = event["bibentries"][bibkey]["title"]
            authors = event["bibentries"][bibkey]["authors"]
            doi = event["bibentries"][bibkey]["doi"]
            pmid = event["bibentries"][bibkey]["pmid"]
            year = event["bibentries"][bibkey]["year"]
            journal = event["bibentries"][bibkey]["journal"]
            print("="*50)
            print("BIBLIOGRAPH ENTRY:")
            print("Title:", title)
            print("Authors:", authors)
            print("DOI:", doi)
            print("PMID:", pmid)
            print("Year:", year)
            print("Journal:", journal)
            print()
            match = occurrence["result"][bibkey]["source_text"]["raw"]
            print(match)
            print()
            if match and ((title and title in match) or (doi and doi in match) or (pmid and pmid in match)):
                correct = True
            else:
                correct = input("\nPRESS ENTER IF CORRECT, ENTER ANY OTHER KEY AND PRESS ENTER IF INCORRECT. ") == ""
            if correct:
                occurrence["method"] = method
                event["first_mentioned"] = occurrence
                reduced_events.append(event)
                break
        
with open(json_path.replace(".json", "_reduced.json"), "w") as file:
    file.write("[" + "\n")
    file.write(",\n".join([dumps(event) for event in reduced_events]))
    file.write("\n" + "]")
