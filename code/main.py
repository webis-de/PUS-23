from bibliography.bibliography import Bibliography
from article import Article
from json import dump, load
from os.path import sep

output_directory = ".." + sep + "results"

#read bibliography from CSV
bibliography = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv")
bibliography.plot_publication_distribution_to_file(output_directory)

#read revisions from wikipedia revision history
article = Article(".." + sep + "extractions" + sep + "CRISPR_en")
article.plot_revision_distribution_to_file(output_directory)

phrases = ["adaptive_immunity","agriculture","application","bolotin","broad_institute","cas_9","controversy",
           "create_new_species","crispr","crispr_cas","crispr_cas_9","crispr_locus","crispr_rnas","crrnas","disease",
           "dna","double_stranded","doudna","e_coli","embryos","ethics","gene edit","gmos","guide_rna","human","marraffini",
           "max_planck_institute","medicine","moineau","mojica","pam","patent","patient","s_thermophilus","sontheimer","talens",
           "technical","technique","technology","tool","tracrrna","type_ii","u_california","u_vienna","upstream","van_der_oost","zhang","zinc"]

#extract tracks of bibkey values in article
tracks = article.track_bibkeys_in_article(["titles", "dois", "authors"], bibliography)

#write and plot results to file
for track in tracks.items():
    article.write_track_to_file(track, output_directory)
    article.plot_track_to_file(track, output_directory)

#extract tracks of phrase lists in article
tracks = article.track_phrases_in_article([phrases])

#write and plot results to file
for track in tracks.items():
    article.write_track_to_file(track, output_directory)
    article.plot_track_to_file(track, output_directory)
