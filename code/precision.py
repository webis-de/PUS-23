from json import load, dumps
from os.path import basename, dirname, sep

json_path = "../analysis/2021_01_25_14_44_39/CRISPR_en_precision.json"

with open(json_path) as file:
    data = load(file)

prec = {}

for event in data:
    for key in event["first_mentioned"]["relaxed"]:
        if key not in prec:
            prec[key] = [0,0]
        if event["first_mentioned"]["relaxed"][key]:
            bibkey = list(event["bibentries"].keys())[0]
            print(bibkey)
            title = event["bibentries"][bibkey]["title"]
            print("="*len(title))
            print(title)
            print()
            print(event["first_mentioned"]["relaxed"][key]["result"][bibkey]["source_text"]["raw"])
            #event["first_mentioned"]["relaxed"][key]["result"]["correct"] = True if input() == "" else False
            if event["first_mentioned"]["relaxed"][key]["result"]["correct"]:
                prec[key][0] += 1
            prec[key][1] += 1

##with open(dirname(json_path) + sep + basename(json_path).split(".")[0] + "_precision.json", "w") as file:
##    file.write("[" + "\n")
##    for event in data:
##        file.write(dumps(event) + "," + "\n")
##    file.write("]")
            
            
