from json import load, dumps
from os.path import basename, dirname, sep

json_path = "../analysis/2021_01_25_14_44_39/CRISPR_en.json"

with open(json_path) as file:
    data = load(file)

prec = {}

for event in data:
    for key in event["first_mentioned"]["relaxed"]:
        if key not in prec:
            prec[key] = [0,0]
        if event["first_mentioned"]["relaxed"][key]:
            bibkey = list(event["bibentries"].keys())[0]
            title = event["bibentries"][bibkey]["title"]
            authors = event["bibentries"][bibkey]["authors"]
            print("="*len(title))
            print("BIBLIOGRAPH ENTRY:")
            print("Title:",title)
            print("Authors:",str(authors))
            print()
            print("MATCH:")
            print(event["first_mentioned"]["relaxed"][key]["result"][bibkey]["source_text"]["raw"])
            print()
            correct = input("\nCORRECT? PRESS ENTER IF CORRECT, PRESS n IF INCORRECT. ")
            if correct:
                prec[key][0] += 1
            prec[key][1] += 1

for key,value in prec.items():
    print(key, round(value[0]/value[1]*100, 2))
            
            
