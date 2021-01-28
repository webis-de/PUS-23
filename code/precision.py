from json import load, dumps
from os.path import basename, dirname, sep
from pprint import pprint

json_path = "../analysis/2021_01_25_14_44_39/CRISPR_en.json"

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
            print("="*50)
            print("BIBLIOGRAPH ENTRY:")
            print("Title:", title)
            print("Authors:", authors)
            print("DOI:", doi)
            print("PMID:", pmid)
            print("Year:", year)
            print("Journal:", journal)
            print()
            match = event["first_mentioned"]["relaxed"][key]["result"][bibkey]["source_text"]["raw"]
            print("MATCH:")
            print(match)
            if match and ((title and title in match) or (doi and doi in match) or (pmid and pmid in match)):
                correct = True
            else:
                correct = input("\nPRESS ENTER IF CORRECT, ENTER ANY OTHER KEY AND PRESS ENTER IF INCORRECT. ")
            if correct:
                precisions[key][0] += 1
            precisions[key][1] += 1

print()

pprint(precisions)

print()

for key,value in precisions.items():
    print(key, round(value[0]/value[1]*100, 2))
            
            
