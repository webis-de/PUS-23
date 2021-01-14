from article.article import Article

article = Article("../articles/2020-12-12/CRISPR_en")

#get revision with id 347670131
revision = article.get_revision(revid=906327294)

print(revision.url, "\n")

#get references
references = revision.get_references()

#get sections
sections = revision.get_sections()

reference = references[1]

print("REFENCE\n", reference.get_text())
print("REFENCE ID\n", reference.get_id())

###find sections reference links to
for section in list(reference.linked_sections(sections)):
    print("\n", section.get_text())
    
