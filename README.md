# Wikipedia CRISPR Innovation Tracing Code

This repository contains information and code concerning the project 'Tracing Innovations on Wikipedia'.

## analysis
- default directory for article analyis runs
  - articles: candidate retrieval and analysis
  - bibliography: reference matching
  - contributors: editor distribution analysis
  - development: character-reference-time plots
  - sections: section analysis
- on gitignore

## articles
- default directory for extractions
- on gitignore

## code
##### main_article.py
- analyse revision as per eventlist and bibliography
- save to JSON Lines and pretty printed TXT file
##### main_candidate.py
- candidate retrieval from revision dumps
- analysis of candidate files based on revision scrapes
##### main_contributors.py
- analyse editor distribution
##### main_diff.py
- diff revisions of article
##### main_heroes.py
- analyse how researchers are mentioned
##### main_revision.py
- detailed view and analysis of revision
##### main_scraper.py
- scrape revision history of an article with HTML
##### main_sections.py
- build article section tree
##### main_timeline.py
- analyse events and accounts
##### article
- classes: Article, Revision, Section, Source, Timestamp
##### bibliography
- classes: Bibentry, Bibliography
##### contribution
- classes: Contribution
##### differ
- classes: Differ (custom word-level differ)
##### evaluation
- evaluation helper scripts
- for candidate retrieval (article) and reference matching (bibliography) results
##### preprocessor
- classes: Preprocessor, Sentenizer, Tokenizer
##### scraper
- scrape revisions of Wikipedia article up to given date and/or count
- downloads HTML and extracts MediaWiki text and categories, discarding boilerplate
- save to JSON Lines file
##### timeline
- classes: Account, AccountList, Event, EventList
##### utility
- classes: WikipediaDumpReader

## data
- account and event CSVs
- bibliography CSV
- problematic revid JSON
- relevant article TXTs

## test
- test scripts

## NOT IN REPOSITORY
### FILES
- https://doi.org/10.5281/zenodo.10507820
- articles and analysis

