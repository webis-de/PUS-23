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

precisions = {method:[0,0] for method in verbatim_methods + relaxed_methods}

with open(json_path) as file:
    events = load(file)

for index, event in enumerate(events):
    bibkey = list(event["bibentries"].keys())[0]
    title = event["bibentries"][bibkey]["title"]
    authors = event["bibentries"][bibkey]["authors"]
    doi = event["bibentries"][bibkey]["doi"]
    pmid = event["bibentries"][bibkey]["pmid"]
    year = event["bibentries"][bibkey]["year"]
    journal = event["bibentries"][bibkey]["journal"]
    no_result = True
    for strategy in event["first_mentioned"]:
        for method,result in event["first_mentioned"][strategy].items():
            if result:
                if method in verbatim_methods:
                    no_result = False
                    precisions[method][0] += 1
                    precisions[method][1] += 1
                else:
                    precisions[method][1] += 1
                    match = result["result"][bibkey]["source_text"]["raw"]
                    if match and ((title and title in match) or (doi and doi in match) or (pmid and pmid in match)):
                        correct = True
                    else:
                        print("="*50)
                        print("BIBLIOGRAPH ENTRY:")
                        print("Title:", title)
                        print("Authors:", authors)
                        print("DOI:", doi)
                        print("PMID:", pmid)
                        print("Year:", year)
                        print("Journal:", journal)
                        print()
                        print(match)
                        print()
                        correct = input("\nENTER y IF CORRECT, PRESS ENTER IF INCORRECT. ") == "y"
                    if correct:
                        no_result = False
                        precisions[method][0] += 1
                    else:
                        events[index]["first_mentioned"][strategy][method] = None
    if no_result:
        events[index] = None
        
with open(json_path.replace(".json", "_annotated.json"), "w") as file:
    file.write("[" + "\n")
    file.write(",\n".join([dumps(event) for event in events if event]))
    file.write("\n" + "]")

with open(dirname(json_path) + sep + "precision.txt", "w") as file:
    for method, score in precisions.items():
        file.write(method + " " + "correct: " + str(score[0]) + "/" + str(score[1]) + " " + str(round(score[0]/score[1]*100, 2)) + "\n")
