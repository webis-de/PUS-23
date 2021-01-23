import matplotlib.pyplot as plt
from os.path import dirname, sep
from json import load
import numpy as np

NO_MATCH_OR_NEGATIVE = 0.05
ZERO = 0.25

def calculate_delay(match_year, event_year):
    if match_year != None:
        delay = match_year - event_year
        if delay < 0:
            return NO_MATCH_OR_NEGATIVE
        else:
            return delay + ZERO
    else:
        return NO_MATCH_OR_NEGATIVE

def stringify_delay(delay):
    if delay == NO_MATCH_OR_NEGATIVE:
        return "-".rjust(20, " ")
    else:
        return str(int(delay - ZERO))

def calculate_delays_and_write_table_and_plot(json_file, skip_no_result):

    data = sorted([event for event in load(open(json_file)) if event["bibentries"]], key=lambda event: int(event["event_year"]))

    bibkey_list = [list(event["bibentries"].keys())[0] for event in data]
    event_year_list = [int(event["event_year"]) if event["event_year"] else None for event in data]

    verbatim_title_list = [int(event["first_mentioned"]["verbatim"]["titles"]["timestamp"][:4]) if event["first_mentioned"]["verbatim"]["titles"] else None for event in data]
    verbatim_doi_list = [int(event["first_mentioned"]["verbatim"]["dois"]["timestamp"][:4]) if event["first_mentioned"]["verbatim"]["dois"] else None for event in data]
    verbatim_pmid_list = [int(event["first_mentioned"]["verbatim"]["pmids"]["timestamp"][:4]) if event["first_mentioned"]["verbatim"]["pmids"] else None for event in data]
    ned_02_list = [int(event["first_mentioned"]["relaxed"]["ned <= 0.2"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned <= 0.2"] else None for event in data]
    ned_03_list = [int(event["first_mentioned"]["relaxed"]["ned <= 0.3"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned <= 0.3"] else None for event in data]
    ned_04_list = [int(event["first_mentioned"]["relaxed"]["ned <= 0.4"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned <= 0.4"] else None for event in data]
    ned_and_exact_list = [int(event["first_mentioned"]["relaxed"]["ned_and_exact"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned_and_exact"] else None for event in data]
    ned_and_jaccard_list = [int(event["first_mentioned"]["relaxed"]["ned_and_jaccard"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned_and_jaccard"] else None for event in data]
    ned_and_ndcg_list = [int(event["first_mentioned"]["relaxed"]["ned_and_ndcg"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned_and_ndcg"] else None for event in data]

    original_lists = [bibkey_list, event_year_list, verbatim_title_list, verbatim_doi_list, verbatim_pmid_list, ned_02_list, ned_03_list, ned_04_list, ned_and_exact_list, ned_and_jaccard_list, ned_and_ndcg_list]

    if skip_no_result:
        value_lists = original_lists[2:]
        reduced_lists = []

        for original_list in original_lists:
            reduced_list = []
            for i in range(len(original_list)):
                if len([value_list[i] for value_list in value_lists if value_list[i]]) > 0:
                    reduced_list.append(original_list[i])
            reduced_lists.append(reduced_list)

        for i in range(len(original_lists)):
            original_lists[i] = reduced_lists[i]

    bibkey_list = original_lists[0]
    event_year_list = original_lists[1]
    verbatim_title_delays = [calculate_delay(match, year) for match,year in zip(original_lists[2], event_year_list)]
    verbatim_doi_delays = [calculate_delay(match, year) for match,year in zip(original_lists[3], event_year_list)]
    verbatim_pmid_delays = [calculate_delay(match, year) for match,year in zip(original_lists[4], event_year_list)]
    ned_02_delays = [calculate_delay(match, year) for match,year in zip(original_lists[5], event_year_list)]
    ned_03_delays = [calculate_delay(match, year) for match,year in zip(original_lists[6], event_year_list)]
    ned_04_delays = [calculate_delay(match, year) for match,year in zip(original_lists[7], event_year_list)]
    ned_and_exact_delays = [calculate_delay(match, year) for match,year in zip(original_lists[8], event_year_list)]
    ned_and_jaccard_delays = [calculate_delay(match, year) for match,year in zip(original_lists[9], event_year_list)]
    ned_and_ndcg_delays = [calculate_delay(match, year) for match,year in zip(original_lists[10], event_year_list)]

    with open(dirname(json_file) + sep + "recall" + "_by_bibkey" + ("_all" if not skip_no_result else "") + ".csv", "w") as file:
        file.write("bibkey" + "," + \
                   "event_year" + "," + \
                   "verbatim_title" + "," + \
                   "verbatim_doi" + "," + \
                   "verbatim_pmid" + "," + \
                   "ned <= 0.2" + "," + \
                   "ned <= 0.3" + "," + \
                   "ned <= 0.4" + "," + \
                   "ned_and_exact" + "," + \
                   "ned_and_jaccard" + "," + \
                   "ned_and_ndcg" + "\n")

        for bibkey, event_year, verbatim_title_delay, verbatim_doi_delay, verbatim_pmid_delay, ned_02_delay, ned_03_delay, ned_04_delay, ned_and_exact_delay, ned_and_jaccard_delay, ned_and_ndcg_delay in \
            zip(bibkey_list, event_year_list, verbatim_title_delays, verbatim_doi_delays, verbatim_pmid_delays, ned_02_delays, ned_03_delays, ned_04_delays, ned_and_exact_delays, ned_and_jaccard_delays, ned_and_ndcg_delays):
            file.write(str(bibkey) + "," + \
                       str(event_year) + "," + \
                       stringify_delay(verbatim_title_delay) + "," + \
                       stringify_delay(verbatim_doi_delay) + "," + \
                       stringify_delay(verbatim_pmid_delay) + "," + \
                       stringify_delay(ned_02_delay) + "," + \
                       stringify_delay(ned_03_delay) + "," + \
                       stringify_delay(ned_04_delay) + "," + \
                       stringify_delay(ned_and_exact_delay) + "," + \
                       stringify_delay(ned_and_jaccard_delay) + "," + \
                       stringify_delay(ned_and_ndcg_delay) + "\n")

    if skip_no_result:
        event_year_list = [str(year) for year in original_lists[1]]
##        year = event_year_list[0]
##        for i in range(1, len(event_year_list)):
##            if event_year_list[i] == year:
##                event_year_list[i] = ""
##            else:
##                year = event_year_list[i]

        width = 0.1
        x = np.arange(len(bibkey_list))
        plt.figure(figsize=(60, 12.5), dpi=200)
        plt.subplots_adjust(bottom=0.15, top=0.99, left=0.01, right=0.998)
        plt.margins(x=0.0005, y=0.005)
        plt.xticks(np.arange(len(bibkey_list)), bibkey_list, rotation=90)
        plt.xlabel("PUBLICATIONS\n(colours represent different matching strategies as per legend | column hints of 0.1 represent no match or false positive (negative delay) | all matches +0.25 to visualise same-year occurrence)")
        plt.ylabel("OCCURRENCE DELAY IN YEARS")
        plt.bar(x - width*4, verbatim_title_delays, width=width, label="verbatim_title")
        plt.bar(x - width*3, verbatim_doi_delays, width=width, label="verbatim_doi")
        plt.bar(x - width*2, verbatim_pmid_delays, width=width, label="verbatim_pmid")
        plt.bar(x - width*1, ned_02_delays, width=width, label="ned <= 0.2")
        plt.bar(x + width*0, ned_03_delays, width=width, label="ned <= 0.3")
        plt.bar(x + width*1, ned_04_delays, width=width, label="ned <= 0.4")
        plt.bar(x + width*2, ned_and_exact_delays, width=width, label="ned_and_exact")
        plt.bar(x + width*3, ned_and_jaccard_delays, width=width, label="ned_and_jaccard")
        plt.bar(x + width*4, ned_and_ndcg_delays, width=width, label="ned_and_ndcg")
        plt.legend()
        plt.savefig(dirname(json_file) + sep + "delays.png")

if __name__ == "__main__":

    json_file = "../analysis/2021_01_22_23_26_37/CRISPR_en.json"
    calculate_delays_and_write_table_and_plot(json_file, False)
    calculate_delays_and_write_table_and_plot(json_file, True)
