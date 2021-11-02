from os.path import basename, dirname, exists, sep
from glob import glob
from json import load, dumps
from utils import parse_json_name, parse_article_title
from csv import reader, writer

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

def get_bibliography_data(event):
    bibkey = list(event["bibentries"].keys())[0]
    title = event["bibentries"][bibkey]["title"]
    authors = event["bibentries"][bibkey]["authors"]
    doi = event["bibentries"][bibkey]["doi"]
    pmid = event["bibentries"][bibkey]["pmid"]
    year = event["bibentries"][bibkey]["year"]
    return (bibkey, title, authors, doi, pmid, year)

def concatenate_bibliography_data(title, authors, doi, pmid, year):
    return ("Title: " + title + "\n" +
            "Authors: " + "[" + ", ".join(authors) + "]" + "\n" +
            "DOI: " + doi + "\n" +
            "PMID: " + pmid + "\n" +
            "Year: " + year)    

json_paths = sorted([path for path
                     in glob("../../analysis/bibliography/2021_11_01/*/*.json")
                     if not any([path.endswith(suffix) for suffix in ["_correct.json", "_annotated.json", "_reduced.json"]])])

to_label_filepath = "../../analysis/bibliography/2021_11_01/to_label.csv"
labelled_filepath =  "../../analysis/bibliography/2021_11_01/labelled.csv"

reference_match_mapping = {}

for json_path in json_paths:

    with open(json_path) as file:
        events = load(file)
    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name)

    print(article_title + ":", json_path)

    if not exists(to_label_filepath):
            
        for index, event in enumerate(events):
            bibkey, title, authors, doi, pmid, year = get_bibliography_data(event)
            concatenated_bibliography_data = concatenate_bibliography_data(title, authors, doi, pmid, year)
            for strategy in event["trace"][article_title]["first_mentioned"]:
                for method,result in event["trace"][article_title]["first_mentioned"][strategy].items():
                    if result:
                        if method in verbatim_methods:
                            continue
                        else:
                            match = result["result"][bibkey]["source_text"]["raw"]
                            if not any([(title and title in match),
                                        (doi and doi in match),
                                        (pmid and pmid in match)]):
                                if concatenated_bibliography_data not in reference_match_mapping:
                                    reference_match_mapping[concatenated_bibliography_data] = {}
                                reference_match_mapping[concatenated_bibliography_data][match] = ""
    else:
        if exists(labelled_filepath):

            reference_match_mapping = {}
            with open(labelled_filepath) as labeled_file:
                csv_reader = reader(labeled_file, delimiter=",")
                for concatenated_bibliography_data,match,judgement in csv_reader:
                    if concatenated_bibliography_data not in reference_match_mapping:
                        reference_match_mapping[concatenated_bibliography_data] = {}
                    reference_match_mapping[concatenated_bibliography_data][match] = bool(int(judgement))
            
            precisions = {method:[0,0] for method in verbatim_methods + relaxed_methods}

            with open(json_path) as file:
                events = load(file)

            for index, event in enumerate(events):
                bibkey, title, authors, doi, pmid, year = get_bibliography_data(event)
                concatenated_bibliography_data = concatenate_bibliography_data(title, authors, doi, pmid, year)
                for strategy in event["trace"][article_title]["first_mentioned"]:
                    for method,result in event["trace"][article_title]["first_mentioned"][strategy].items():
                        if result:
                            if method in verbatim_methods:
                                precisions[method][0] += 1
                                precisions[method][1] += 1
                                events[index]["trace"][article_title]["first_mentioned"][strategy][method]["correct"] = True
                            else:
                                match = result["result"][bibkey]["source_text"]["raw"]
                                if any([(title and title in match),
                                        (doi and doi in match),
                                        (pmid and pmid in match)]):
                                    correct = True
                                else:
                                    correct = reference_match_mapping[concatenated_bibliography_data][match]
                                if correct:
                                    precisions[method][0] += 1
                                precisions[method][1] += 1
                                events[index]["trace"][article_title]["first_mentioned"][strategy][method]["correct"] = correct

            first_event = True
            first_correct_event = True
            first_reduced_event = True
                    
            with open(json_path.replace(".json", "_annotated.json"), "w") as annotated_file,\
                 open(json_path.replace(".json", "_correct.json"), "w") as correct_file,\
                 open(json_path.replace(".json", "_reduced.json"), "w") as reduced_file:
                annotated_file.write("[")
                correct_file.write("[")
                reduced_file.write("[")

                for event in events:

                    annotated_file.write("," * (not first_event) + "\n")
                    first_event = False
                    
                    annotated_file.write(dumps(event))
                    
                    for strategy in event["trace"][article_title]["first_mentioned"]:
                        for method in event["trace"][article_title]["first_mentioned"][strategy]:
                            if event["trace"][article_title]["first_mentioned"][strategy][method] and not event["trace"][article_title]["first_mentioned"][strategy][method]["correct"]:
                                event["trace"][article_title]["first_mentioned"][strategy][method] = None

                    methods_with_results = [item for item in event["trace"][article_title]["first_mentioned"]["verbatim"].values() if item] + \
                                           [item for item in event["trace"][article_title]["first_mentioned"]["relaxed"].values() if item]
                    
                    if any(methods_with_results):

                        correct_file.write("," * (not first_correct_event) + "\n")
                        first_correct_event = False
                        
                        correct_file.write(dumps(event))

                        correct_methods = [item for item in methods_with_results if item["correct"]]
                        
                        if any(correct_methods):
                            earliest_result = sorted(correct_methods, key = lambda item: item["index"])[0]
                            event["trace"][article_title]["first_mentioned"] = earliest_result

                            reduced_file.write("," * (not first_reduced_event) + "\n")
                            first_reduced_event = False
                                
                            reduced_file.write(dumps(event))

                annotated_file.write("\n" + "]")
                correct_file.write("\n" + "]")
                reduced_file.write("\n" + "]")

            with open(json_path.replace(".json", "_precision.csv"), "w") as precision_file:
                precision_csv_writer = writer(precision_file, delimiter=",")
                for method, score in precisions.items():
                    precision_csv_writer.writerow([method, str(score[0]), str(score[1]), str(round(score[0]/score[1]*100, 2)) if score[1] > 0 else "0.0"])

if not exists(to_label_filepath):
    with open(to_label_filepath, "w") as to_label_file:
        to_label_csv_writer = writer(to_label_file, delimiter=",")
        for concatenated_bibliography_data,matches in reference_match_mapping.items():
            for match in matches:
                to_label_csv_writer.writerow([concatenated_bibliography_data, match, ""])
