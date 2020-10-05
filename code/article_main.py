from entity.article import Article

##########################################################
# This file serves as an entry point to test the Article.#
##########################################################


if __name__ == "__main__":

    """
    Open scraped article.
    """
    article = Article("../extractions/CRISPR_de")

    """
    Print text from html.
    """
    print("TEXT\n")
    print(article.revisions[0].get_text().strip())
    print("="*50)
    
    """
    Print references from html.
    """
    print("REFERENCES\n")
    references = article.revisions[0].get_references()
    print("\n\n".join(["\n".join([text.strip() for text in reference.itertext()]) for reference in references]))
    print("="*50)

    """
    Print all titles in references.
    """
    print(article.revisions[0].get_titles())
