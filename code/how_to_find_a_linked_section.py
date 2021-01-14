from article.article import Article

article = Article("../articles/2020-12-12/CRISPR_en")

revision = article.get_revision(revid=347670131)

print(revision.url)
print()

reference = revision.get_references()[0]

print(reference.get_text())
print()

print(list(reference.linked_sections(revision.get_paragraphs()))[0].get_text())
