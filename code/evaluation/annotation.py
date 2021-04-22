from os.path import basename, dirname, sep
from json import load, dumps
from path import JSON

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

with open(JSON) as file:
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
                    events[index]["first_mentioned"][strategy][method]["correct"] = True
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
                        print("->", "METHOD:", method)
                        print("->", "SCORE:", result["result"][bibkey][list(result["result"][bibkey].keys())[-1]])
                        print()
                        print(match)
                        print()
                        correct = input("\nENTER y IF CORRECT, PRESS ENTER IF INCORRECT. ") == "y"
                    if correct:
                        no_result = False
                        precisions[method][0] += 1
                        events[index]["first_mentioned"][strategy][method]["correct"] = True
                    else:
                        events[index]["first_mentioned"][strategy][method]["correct"] = False

##first_event = True
##first_correct_event = True
##first_reduced_event = True
##        
##with open(JSON.replace(".json", "_annotated.json"), "w") as annotated_file,\
##     open(JSON.replace(".json", "_correct.json"), "w") as correct_file,\
##     open(JSON.replace(".json", "_reduced.json"), "w") as reduced_file:
##    annotated_file.write("[")
##    correct_file.write("[")
##    reduced_file.write("[")
##
##    for event in events:
##
##        annotated_file.write("," * (not first_event) + "\n")
##        first_event = False
##        
##        annotated_file.write(dumps(event))
##        
##        for strategy in event["first_mentioned"]:
##            for method in event["first_mentioned"][strategy]:
##                if event["first_mentioned"][strategy][method] and not event["first_mentioned"][strategy][method]["correct"]:
##                    event["first_mentioned"][strategy][method] = None
##
##        methods_with_results = [item for item in event["first_mentioned"]["verbatim"].values() if item] + \
##                               [item for item in event["first_mentioned"]["relaxed"].values() if item]
##        
##        if any(methods_with_results):
##
##            correct_file.write("," * (not first_correct_event) + "\n")
##            first_correct_event = False
##            
##            correct_file.write(dumps(event))
##
##            correct_methods = [item for item in methods_with_results if item["correct"]]
##            
##            if any(correct_methods):
##                earliest_result = sorted(correct_methods, key = lambda item: item["index"])[0]
##                event["first_mentioned"] = earliest_result
##
##                reduced_file.write("," * (not first_reduced_event) + "\n")
##                first_reduced_event = False
##                    
##                reduced_file.write(dumps(event))
##
##    annotated_file.write("\n" + "]")
##    correct_file.write("\n" + "]")
##    reduced_file.write("\n" + "]")
##
##with open(dirname(JSON) + sep + "precision.txt", "w") as file:
##    for method, score in precisions.items():
##        file.write(method + " " + "correct: " + str(score[0]) + "/" + str(score[1]) + " " + str(round(score[0]/score[1]*100, 2)) + "\n")
