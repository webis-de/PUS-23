from article.article import Article
from contributors.contributors import Contributors
from pprint import pprint

from datetime import datetime

def table_contribututions(contributions, file):
    contributions = sorted([(k,v) for k,v in contributions.items()], key=lambda item:item[1][0], reverse=True)
    header = "user".rjust(50, " ") + "absolute".rjust(20, " ") + "relative".rjust(20, " ")
    file.write("\n" + header + "\n")
    file.write("-" * len(header) + "\n")
    for contribution in contributions:
        file.write(str(contribution[0]).rjust(50, " ") + str(str(contribution[1][0])).rjust(20, " ") + str(str(contribution[1][1])).rjust(20, " ") + "\n")

if __name__ == "__main__":

    start = datetime.now()

    with open("revision_contributions.txt", "w") as file:

        article = Article("../articles/2020-12-12/CRISPR_en")

        revisions = article.yield_revisions()

        revision = next(revisions, None)
        file.write(str(revision.index) + " " + revision.url + " " + "\n")
        contributors = Contributors(revision.get_text())
        contributors.align(revision.user)
        ##for part in contributors.parts():
        ##    pprint({part[1]:part[0]})
        table_contribututions(contributors.contributions(), file)

        while revision:

            print(revision.index)
            
            file.write("="*100 + "\n")
            revision = next(revisions, None)

            if revision:
                file.write(str(revision.index) + " " + revision.url + " " + "\n")
                next_contributors = Contributors(revision.get_text())
                next_contributors.align(revision.user, contributors)
                ##for part in next_contributors.parts():
                ##    pprint({part[1]:part[0]})
                table_contribututions(next_contributors.contributions(), file)
                contributors = next_contributors

    end = datetime.now()

    print(end - start)
