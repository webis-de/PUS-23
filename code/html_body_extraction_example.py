from requests import get
from lxml import etree
from re import sub, S
from os import remove, system
from time import sleep

def extract_article_body(url, name):
    #system("firefox '" + url + "'")
    
    html = get(url).text

    tree   = etree.HTML(html)

    try:
        mediawiki_parser_output = tree.findall(".//div[@class='mw-parser-output']")[0]
        mediawiki_parser_output = etree.tostring(mediawiki_parser_output).decode("utf-8")
        mediawiki_parser_output = sub(r"<!--.*?-->", "", mediawiki_parser_output, flags=S)
    except IndexError:
        mediawiki_parser_output = ""

    filename = name + ".html"
    
    with open(filename, "w") as file:
        file.write(mediawiki_parser_output)

    #system("firefox " + filename)

    #sleep(0.5)

    #remove(filename)

if __name__ == "__main__":

    revisions = {"CRISPR_de_first_rev":"https://de.wikipedia.org/w/index.php?title=CRISPR&oldid=69137443",
             "CRISPR_en_first_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=17918488",
             "CRISPR_en_remov_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=898138824"}
    
    for revision in revisions.items():
        extract_article_body(revision[1], revision[0])
