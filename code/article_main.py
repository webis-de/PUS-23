from entity.article import Article
from entity.eventlist import EventList
from entity.accountlist import AccountList
from entity.bibliography import Bibliography
from utility.utils import flatten_list_of_lists
from preprocessor.preprocessor import Preprocessor
from re import findall

##################################################################
# This file serves as an entry point to test the entire pipeline.#
##################################################################

def occurrence(revision):
    return ["index: " + str(revision.index), "url: " + revision.url, "timestamp: " + revision.timestamp_pretty_string()]

if __name__ == "__main__":

    language = "en"
    article = Article("../extractions/CRISPR_" + language)
    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_events - accounts.csv")
    eventlist = EventList("../data/CRISPR_events - events.csv", bibliography, accountlist)
    preprocessor = Preprocessor(language)

    revisions = article.yield_revisions()

    count = 1

    revision = next(revisions, None)
    
    while revision:
        
        print(count)
        count += 1

        #sentenized_text = preprocessor.preprocess(revision.get_text(), lower=True, stopping=False, sentenize=True, tokenize=False)
        paragraphs_and_captions = revision.get_paragraphs() + revision.get_captions()
        referenced_dois = set(flatten_list_of_lists(revision.get_referenced_dois(revision.get_references())))
        referenced_titles = set([title.lower() for title in revision.get_referenced_titles("en", revision.get_references())])
        
        for event in eventlist.events:

            for event_doi in event.dois:
                if not event.first_occurrence["dois"][event_doi]:
                    if event_doi in referenced_dois:
                        event.first_occurrence["dois"][event_doi] = occurrence(revision)

            if event.dois and not event.first_occurrence["all_dois"]:
                #iterate over all event dois
                for event_doi in event.dois:
                    #break if event doi not referenced
                    if event_doi not in referenced_dois:
                        break
                else:
                    #add rivision if all dois occur
                    event.first_occurrence["all_dois"] = occurrence(revision)

            for event_title in event.titles:
                if not event.first_occurrence["titles"][event_title]["full"]:
                    if event_title.lower() in referenced_titles:
                        event.first_occurrence["titles"][event_title]["full"] = occurrence(revision)
                if not event.first_occurrence["titles"][event_title]["processed"]:
                    preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
                    for referenced_title in referenced_titles:
                        referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
                        match_count = sum([1 if word in referenced_title else 0 for word in preprocessed_event_title])
                        if match_count >= len(preprocessed_event_title) * 0.8:
                            event.first_occurrence["titles"][event_title]["processed"] = occurrence(revision)
                            break

            if event.titles and not event.first_occurrence["all_titles"]["full"]:
                #iterate over all event titles
                for event_title in event.titles:
                    #break if event event_title not referenced
                    if event_title.lower() not in referenced_titles:
                        break
                else:
                    #add rivision if all titles occur
                    event.first_occurrence["all_titles"]["full"] = occurrence(revision)

            if event.titles and not event.first_occurrence["all_titles"]["processed"]:
                #iterate over all event titles
                for event_title in event.titles:
                    #tokenize event title
                    event_title = preprocessor.preprocess(event_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
                    #iterate over all referenced titles
                    for referenced_title in referenced_titles:
                        #tokenize referenced title
                        referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
                        #break if 80% of words in event title occur in referenced title
                        match_count = sum([1 if word in referenced_title else 0 for word in event_title])
                        if match_count >= len(event_title) * 0.8:
                            break
                    else:
                        #event title does not occur in referenced titles
                        break
                else:
                    #add revision if all titles occur
                    event.first_occurrence["all_titles"]["processed"] = occurrence(revision)

            if event.keywords and not event.first_occurrence["all_keywords"]:
                for section in paragraphs_and_captions:
                    for keyword in event.keywords:
                        if not findall(keyword, section.text()):
                            #break if keyword not in sentence
                            break
                    else:
                        #else add revision
                        event.first_occurrence["all_keywords"] = occurrence(revision)
                        break
                     
        revision = next(revisions, None)

    with open("article_extraction.txt", "w") as file:
        file.write(("\n"+"-"*50+"\n").join([str(event) for event in eventlist.events]))
