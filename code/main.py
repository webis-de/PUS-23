from entity.bibliography import Bibliography
from entity.article import Article
from scraper.scraper import Scraper
from utility.logger import Logger
from os.path import sep

output_directory = ".." + sep + "results"

#read bibliography from CSV
bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")
bibliography.plot_publication_distribution_to_file(output_directory)

#read revisions from wikipedia revision history (scrape CRISPR article if not present)
try:
    article = Article(".." + sep + "extractions" + sep + "CRISPR_en")
except FileNotFoundError:
    with Scraper(Logger(), "CRISPR", "en") as scraper:
        scraper.scrape(".." + sep + "extractions", False)
    article = Article(".." + sep + "extractions" + sep + "CRISPR_en")
article.plot_revision_distribution_to_file(output_directory)

phrases = ["adaptive immunity","agriculture","application","bolotin","broad institute","cas 9","controversy",
           "create new species","crispr","crispr cas","crispr cas 9","crispr locus","crispr rnas","crrnas","disease",
           "dna","double-stranded","doudna","e. coli","embryos","ethics","gene edit","gmos","guide rna","human","marraffini",
           "max planck institute","medicine","moineau","mojica","pam","patent","patient","s. thermophilus","sontheimer","talens",
           "technical","technique","technology","tool","tracrrna","type ii","u california","u vienna","upstream","van der oost","zhang","zinc"]

#extract tracks of field values for each bibentry in bibliography from article
tracks = article.track_field_values_in_article(["titles", "dois", "authors"], bibliography)

#write and plot results to file
for track in tracks.items():
    article.write_track_to_file(track, output_directory)
    article.plot_track_to_file(track, output_directory)

#extract tracks of phrase lists from article
tracks = article.track_phrases_in_article([phrases])

#write and plot results to file
for track in tracks.items():
    article.write_track_to_file(track, output_directory)
    article.plot_track_to_file(track, output_directory)
