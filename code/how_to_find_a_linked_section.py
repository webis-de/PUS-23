from article.article import Article

article = Article("../articles/2020-12-12/CRISPR_en")

#get revision with id 347670131
revision = article.get_revision(revid=347670131)

print(revision.url, "\n")

#take first reference
reference = revision.get_references()[0]

print(reference.get_text(), "\n")

#get sections
sections = revision.get_sections()

#find section reference links to
print(list(reference.linked_sections(sections))[0].get_text())
