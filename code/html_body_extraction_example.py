from requests import get
from lxml import etree
from re import sub, S
from os import remove, system
from time import sleep

revisions = {"CRISPR_de_first_rev":"https://de.wikipedia.org/w/index.php?title=CRISPR&oldid=69137443",
             "CRISPR_en_first_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=17918488",
             "CRISPR_en_remov_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=898138824"}

def extract_article_body(url, name):
    system("firefox '" + url + "'")
    
    html = get(url).text

    tree   = etree.HTML(html)

    try:
        content = etree.tostring(tree.findall(".//div[@class='mw-parser-output']")[0])
        cleaned_content = content.decode("utf-8")
        result = sub(r"<!--.*-->","", cleaned_content, flags=S)
    except IndexError:
        result = ""

    filename = name + ".html"
    
    with open(filename, "w") as file:
        file.write(result)

    system("firefox " + filename)

    sleep(0.5)

    remove(filename)

for revision in revisions.items():
    extract_article_body(revision[1], revision[0])
