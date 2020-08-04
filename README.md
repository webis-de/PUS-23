# Science Analytics Wikipedia

This repository contains information and code concerning Science Analytics Wikipedia.

### documents

##### tracing-innovations-on-wikipedia (Benno)
- https://docs.google.com/document/d/1QBe9mvq0BlYRzYDi0ul97GLRB8nibWsjxA7uUFYTino
##### Timeline_Crispr_cas (Marion)
- https://docs.google.com/spreadsheets/d/1so4jyyjT62wzqMe_l7rpa94QhAWurNtSYed2oGSphoM/edit#gid=0
##### CRISPR_events (Arno)
- https://docs.google.com/spreadsheets/d/1wRwgRmMYluVJPrr_p-BKn6fycDGmZ_JdlI-5dWUKnMw/edit#gid=1179906549
##### Manuscript_STHV (Arno)
- https://docs.google.com/document/d/1KOKK47m_EJqCqUsBGf9ZDlUKeSqTjJbd6yIgCjuS1K8/edit?ts=5f292f2a#heading=h.bs1md45veld8

### cvs

- proposals-in-progress/BMBF-indikatorik-19-today
- research-in-progress/computational-social-science/CONF-20/science-analytics-wikipedia

### code

- read xml file of revision history of Wikipedia article
- read bibliography csv
- track bibentry value occurance in revision history
- write results to file and plot timelines
- plot revision and bibliography distribution
- read timeline csv (timeline subdirectory; deprecated)
- scraper to get all revisions of an article from wikipedia as line JSON

### data

- CRISPR_en.xml: revision history of English Wikipedia article on CRISPR
- CRISPR_de.xml: revision history of German Wikipedia article on CRISPR
- Referenzen_crispr_cas.csv: bibliography related to Crispr Cas
- Timeline_Crispr_Cas.ods: ODS version of Crispr Cas timeline by Marion
- Timeline_Crispr_Cas.csv: CSV version of Crispr Cas timeline by Marion

### results

- sample extractions and plots of English Wikipedia article CRISPR

### notes

- revision histories of up to 1000 edits can be extracted via https://en.wikipedia.org/wiki/Special:Export and https://de.wikipedia.org/wiki/Spezial:Exportieren respectively

