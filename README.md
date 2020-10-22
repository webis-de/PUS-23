# Science Analytics Wikipedia

This repository contains information and code concerning Science Analytics Wikipedia.

### documents

##### tracing-innovations-on-wikipedia (Benno)
- https://docs.google.com/document/d/1QBe9mvq0BlYRzYDi0ul97GLRB8nibWsjxA7uUFYTino
##### Timeline_Crispr_cas (Marion)
- https://docs.google.com/spreadsheets/d/1so4jyyjT62wzqMe_l7rpa94QhAWurNtSYed2oGSphoM
##### CRISPR_events (Arno)
- https://docs.google.com/spreadsheets/d/1wRwgRmMYluVJPrr_p-BKn6fycDGmZ_JdlI-5dWUKnMw
##### Manuscript_STHV (Arno)
- https://docs.google.com/document/d/1KOKK47m_EJqCqUsBGf9ZDlUKeSqTjJbd6yIgCjuS1K8

### files
- https://files.webis.de/wikipedia-tracing-innovations/

### cvs

- proposals-in-progress/BMBF-indikatorik-19-today
- research-in-progress/computational-social-science/CONF-20/science-analytics-wikipedia

### code

- scrape all revisions of article from Wikipedia as line JSON, update existing revision extractions
- track bibentry value and phrase occurance in revision history and write results to file and plot timelines
- plot revision and bibliography distribution

### data

- bibliography_marion.bib: bibliography related to Crispr Cas (BibTex) as compiled by Marion
- wikipedia_articles.json: relevant Wikipedia article titles as compiled by Arno

### articles

- default directory for extractions
- on gitignore

## analysis

- default directory for article analyis runs
- on gitignore

### results

- sample extractions and plots of English Wikipedia article CRISPR

### notes

- revision histories of up to 1000 edits can be extracted via https://en.wikipedia.org/wiki/Special:Export and https://de.wikipedia.org/wiki/Spezial:Exportieren respectively
- Scraper uses Wikimedia API

