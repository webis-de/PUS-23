from bibliography import Bibliography
from article import Article
from json import dump, load
from os.path import sep
from pprint import pprint

output_directory = ".." + sep + "results"

#read bibliography from CSV
bibliography = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv")
bibliography.plot_publication_distribution_to_file(output_directory)

#read revisions from wikipedia revision history
article = Article(".." + sep + "data" + sep + "CRISPR_en.xml")
article.plot_revision_distribution_to_file(output_directory)

#extract tracks of bibkey values in article
bibkey_tracks = article.track_bibkeys_in_article(["titles", "dois", "authors"], bibliography)
#phrase_tracks = article.track_phrases_in_article([["gene editing", "crispr cas", "medicine", "cancer", "science"]])

#write and plot results to file
for track in bibkey_tracks.items():
    article.write_track_to_file(bibkey_tracks, output_directory)
    article.plot_track_to_file(track, output_directory)

