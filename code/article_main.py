from entity.article import Article
from pprint import pprint

##########################################################
# This file serves as an entry point to test the Article.#
##########################################################


if __name__ == "__main__":

    """
    Open scraped article.
    """
    article = Article("../extractions/CRISPR_de")

    """
    Print extracted HTML.
    """
    pprint(article.revisions[0].html, width=300)

