from requests import get
from lxml import etree
from re import sub

revisions = {"CRISPR_de_first_rev":"https://de.wikipedia.org/w/index.php?title=CRISPR&oldid=69137443",
             "CRISPR_en_first_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=17918488"}

def extract_article_body(url, name):
    res = get(url)

    tree   = etree.HTML(res.text)

    result = etree.tostring(tree.findall(".//div[@class='mw-parser-output']")[0])

    string = result.decode("utf-8").replace("\n","")
    string = sub(r"<!--.*-->","", string)

    with open(name + ".html", "w") as file:
        file.write(string)

for revision in revisions.items():
    extract_article_body(revision[1], revision[0])
