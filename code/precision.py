from json import load, dumps
from os.path import basename, dirname, sep
from pprint import pprint

json_path = "../analysis/FOOBAR/2021_01_28_18_35_00/CRISPR_de.json"

with open(json_path) as file:
    data = load(file)

precisions = {}

for event in data:
    for key in event["first_mentioned"]["relaxed"]:
        if key not in precisions:
            precisions[key] = [0,0]
        if event["first_mentioned"]["relaxed"][key]:
            bibkey = list(event["bibentries"].keys())[0]
            print("="*50)
            print("BIBLIOGRAPH ENTRY:")
            print("Title:", event["bibentries"][bibkey]["title"])
            print("Authors:",event["bibentries"][bibkey]["authors"])
            print("DOI:",event["bibentries"][bibkey]["doi"])
            print("PMID:",event["bibentries"][bibkey]["pmid"])
            try:
                print("Journal:",event["bibentries"][bibkey]["journal"])
            except KeyError:
                pass
            print()
            print("MATCH:")
            print(event["first_mentioned"]["relaxed"][key]["result"][bibkey]["source_text"]["raw"])
            print()
            correct = input("PRESS ENTER IF CORRECT, ENTER ANY OTHER KEY AND PRESS ENTER IF INCORRECT. ")
            if correct:
                precisions[key][0] += 1
            precisions[key][1] += 1

print()

pprint(precisions)

print()

for key,value in precisions.items():
    print(key, round(value[0]/value[1]*100, 2))
            
            
