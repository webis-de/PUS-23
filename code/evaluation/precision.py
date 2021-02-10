from json import load, dumps
from os.path import basename, dirname, sep
from pprint import pprint
from path import json_path

with open(json_path) as file:
    data = load(file)

precisions = {}

for event in data:
    for key in event["first_mentioned"]["relaxed"]:
        if key not in precisions:
            precisions[key] = [0,0]
        if event["first_mentioned"]["relaxed"][key]:
            bibkey = list(event["bibentries"].keys())[0]
            title = event["bibentries"][bibkey]["title"]
            authors = event["bibentries"][bibkey]["authors"]
            doi = event["bibentries"][bibkey]["doi"]
            pmid = event["bibentries"][bibkey]["pmid"]
            year = event["bibentries"][bibkey]["year"]
            try:
                journal = event["bibentries"][bibkey]["journal"]
            except KeyError:
                journal = None
            match = event["first_mentioned"]["relaxed"][key]["result"][bibkey]["source_text"]["raw"]

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
                print("MATCH:")
                print(match)
                correct = input("\nPRESS ENTER IF CORRECT, ENTER ANY OTHER KEY AND PRESS ENTER IF INCORRECT. ") == ""
            if correct:
                precisions[key][0] += 1
            precisions[key][1] += 1

print()

with open(dirname(json_path) + sep + "precision.txt", "w") as file:
    for key, value in precisions.items():
        file.write(key + " " + "correct: " + str(value[0]) + "/" + str(value[1]) + " " + str(round(value[0]/value[1]*100, 2)) + "\n")
            
            
