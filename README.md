# Science Analytics Wikipedia

This repository contains information and code concerning the project 'Tracing Innovations on Wikipedia'.

## analysis
- default directory for article analyis runs
  - bibliography: reference matching
  - contributors: editor distribution analysis
  - development: character-reference-time plots
  - heroes: import researchers
  - sections: section analysis
- on gitignore

## articles
- default directory for extractions
- on gitignore

## code
##### main_article.py
- analyse revision as per eventlist and bibliography
- save to JSON Lines and pretty printed TXT file
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
- article, revision, section, source
##### bibliography
- bibentry, bibliography
##### contribution
- contribution
##### differ
- custom word-level differ
##### evaluation
- evaluation helper scripts
##### scraper
- scrape revisions of Wikipedia article up to given date and/or count
- downloads HTML and extracts MediaWiki text and categories, discarding boilerplate
- save to JSON Lines file
##### timeline
- account and event
##### utility
- logger and other utility functions

## data
- account and event CSVs
- bibliography BIB
- problematic revid JSON

## test
- test scripts

## NOT IN REPOSITORY
### FILES
- https://files.webis.de/wikipedia-tracing-innovations
- articles and analysis

### CVS
- proposals-in-progress/BMBF-indikatorik-19-today
- research-in-progress/computational-social-science/CONF-20/science-analytics-wikipedia

