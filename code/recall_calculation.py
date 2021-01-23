from json import load
from os.path import dirname, sep

def calculate_and_write_recall_table(json_path, sort):

    with open(json_path) as file:
        data = [event for event in load(file) if event["account"]]

    account_ids = sorted(set([event["account"]["account_id"] for event in data]), key = lambda x: int(x))

    if sort:
        publication_events_by_account = {account_id:[] for account_id in account_ids}

        for publication_event in data:
            publication_events_by_account[publication_event["account"]["account_id"]].append(publication_event)
    else:
        publication_events_by_account = {"ALL ACOUNT IDs":[] for account_id in account_ids}

        for publication_event in data:
            publication_events_by_account["ALL ACOUNT IDs"].append(publication_event)   

    with open(dirname(json_path) + sep + "recall" + ("_by_account" if sort else "") + ".csv", "w") as file:
        for account_id, publication_events in publication_events_by_account.items():

            file.write("Account ID: " + str(account_id) + "\n")
            file.write("\n")
            results = {"any": {"data":
                               [item for item in publication_events if
                                item["first_mentioned"]["verbatim"]["titles"] or
                                item["first_mentioned"]["verbatim"]["dois"] or 
                                item["first_mentioned"]["verbatim"]["pmids"] or
                                item["first_mentioned"]["relaxed"]["ned <= 0.2"] or
                                item["first_mentioned"]["relaxed"]["ned <= 0.3"] or
                                item["first_mentioned"]["relaxed"]["ned <= 0.4"] or
                                item["first_mentioned"]["relaxed"]["ned_and_exact"] or
                                item["first_mentioned"]["relaxed"]["ned_and_jaccard"] or
                                item["first_mentioned"]["relaxed"]["ned_and_ndcg"]],
                               "note":
                               "any of the strategies below"},
                       "title.exact": {"data":
                                       [item for item in publication_events if item["first_mentioned"]["verbatim"]["titles"]],
                                       "note":
                                       "each title occurs verbatim in revision"},
                       "dois": {"data":
                                [item for item in publication_events if item["first_mentioned"]["verbatim"]["dois"]],
                                "note":
                                "each doi occurs verbatim in revision"},
                       "pmids": {"data":
                                 [item for item in publication_events if item["first_mentioned"]["verbatim"]["pmids"]],
                                 "note":
                                 "each pmid occurs verbatim in a source (element in References or Further Reading)"},
                       "ned <= 0.2": {"data":
                                     [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned <= 0.2"]],
                                     "note":
                                     "for each title there is a source with a title with normalised edit distance <= 0.2"},
                       "ned <= 0.3": {"data":
                                     [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned <= 0.3"]],
                                     "note":
                                     "for each title there is a source with a title with normalised edit distance <= 0.3"},
                       "ned <= 0.4": {"data":
                                     [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned <= 0.4"]],
                                     "note":
                                     "for each title there is a source with a title with normalised edit distance <= 0.4"},
                       "ned_and_exact": {"data":
                                     [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned_and_exact"]],
                                     "note":
                                     "for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with ratio >= 1.0"},
                       "ned_and_jaccard": {"data":
                                         [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned_and_jaccard"]],
                                         "note":
                                         "for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with Jaccard Index >= 0.8"},
                       "ned_and_ndcg": {"data":
                                        [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned_and_ndcg"]],
                                        "note":
                                        "for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with nDCG >= 0.8"}
                       }


            file.write("number of events" + "," + str(len(publication_events)) + "\n")
            file.write("\n")
            file.write("Strategy Employed to Identify First Occurrence" + "," + "Absolute" + "," + "Relative" + "," + "Notes" + "\n")
            for key,value in results.items():
                file.write(key + "," + str(len(value["data"])) + "," + str(round(len(value["data"])/len(publication_events)*100, 2)) + "," + value["note"] + "\n")
                if key == "any":
                    file.write("Verbatim Match Measures" + "\n")
                elif key == "pmids":
                    file.write("Relaxed Match Measures" + "\n")
            file.write("\n")

if __name__ == "__main__":

    calculate_and_write_recall_table("../analysis/2021_01_22_23_26_37/CRISPR_en.json", False)
    calculate_and_write_recall_table("../analysis/2021_01_22_23_26_37/CRISPR_en.json", True)


