from json import load

with open("CRISPR_en.json") as file:
    data = [event for event in load(file) if event["account"]]

account_ids = sorted(set([event["account"]["account_id"] for event in data]), key = lambda x: int(x))

SORT_BY_ACCOUNT_ID = True

if SORT_BY_ACCOUNT_ID:
    publication_events_by_account = {account_id:[] for account_id in account_ids}

    for publication_event in data:
        publication_events_by_account[publication_event["account"]["account_id"]].append(publication_event)
else:
    publication_events_by_account = {"ALL ACOUNT IDs":[] for account_id in account_ids}

    for publication_event in data:
        publication_events_by_account["ALL ACOUNT IDs"].append(publication_event)   

with open("analysis.csv", "w") as file:
    for account_id, publication_events in publication_events_by_account.items():

        file.write("Account ID: " + account_id + "\n")
        file.write("\n")
        results = {"any": {"data":
                           [item for item in publication_events if
                           item["first_mentioned"]["titles"]["exact_match"] or
                           item["first_mentioned"]["titles"]["ned"] or
                           item["first_mentioned"]["authors"]["exact_match"] or
                           item["first_mentioned"]["authors"]["jaccard"] or
                           item["first_mentioned"]["authors"]["ndcg"] or
                           item["first_mentioned"]["dois"] or
                           item["first_mentioned"]["pmids"]],
                           "note":
                           "any of the strategies below"},
                   "title.exact": {"data":
                                   [item for item in publication_events if item["first_mentioned"]["titles"]["exact_match"]],
                                   "note":
                                   "each title occurs verbatim in revision"},
                   "dois": {"data":
                            [item for item in publication_events if item["first_mentioned"]["dois"]],
                            "note":
                            "each doi occurs verbatim in revision"},
                   "pmids": {"data":
                             [item for item in publication_events if item["first_mentioned"]["pmids"]],
                             "note":
                             "each pmid occurs verbatim in a source (element in References or Further Reading)"},
                   "title.ned": {"data":
                                 [item for item in publication_events if item["first_mentioned"]["titles"]["ned"]],
                                 "note":
                                 "for each title there is a source with a title with normalised edit distance <= 0.2"},
                   "authors.exact": {"data":
                                     [item for item in publication_events if item["first_mentioned"]["authors"]["exact_match"]],
                                     "note":
                                     "for each list of authors there is a source with a list of authors with ratio >= 1.0"},
                   "authors.jaccard": {"data":
                                       [item for item in publication_events if item["first_mentioned"]["authors"]["jaccard"]],
                                       "note":
                                       "for each list of authors there is a source with a list of authors with Jaccard Index >= 0.8"},
                   "authors.ndcg": {"data":
                                    [item for item in publication_events if item["first_mentioned"]["authors"]["ndcg"]],
                                    "note":
                                     "for each list of authors there is a source with a list of authors with nDCG >= 0.8"},
                   "title.ned ∧ (authors.exact ∨ authors.jaccard ∨ authors.ndcg)": {"data":
                                                                                        [item for item in publication_events if
                                                                                         item["first_mentioned"]["titles"]["ned"] and
                                                                                         (item["first_mentioned"]["authors"]["exact_match"] or
                                                                                          item["first_mentioned"]["authors"]["jaccard"] or
                                                                                          item["first_mentioned"]["authors"]["ndcg"])],
                                                                                        "note":
                                                                                        "combination of relaxed title search and any of the relaxed author measures above"
                                                                                        }
                   }


        file.write("number of events of type 'publication' with bib_keys" + "," + str(len(publication_events)) + "\n")
        file.write("\n")
        file.write("Strategy Employed to Identify First Occurrence" + "," + "Absolute" + "," + "Relative" + "," + "Notes" + "\n")
        for key,value in results.items():
            file.write(key + "," + str(len(value["data"])) + "," + str(round(len(value["data"])/len(publication_events)*100, 2)) + "," + value["note"] + "\n")
            if key == "any":
                file.write("Exact Match Measures" + "\n")
            elif key == "pmids":
                file.write("Relaxed Match Measures" + "\n")
        file.write("\n")
