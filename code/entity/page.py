from requests import get
from lxml import etree
from re import sub, S
from os import remove, system
from time import sleep

class Page:

    def __init__(self, title, url):

        self.title = title
        self.url = url
        self.html = get(self.url).text
        self.tree = etree.HTML(self.html)

    def get_mediawiki_parser_output(self):
        try:
            mediawiki_parser_output = self.tree.findall(".//div[@class='mw-parser-output']")[0]
            mediawiki_parser_output = etree.tostring(mediawiki_parser_output).decode("utf-8")
            return sub(r"<!--.*?-->", "", mediawiki_parser_output, flags=S)
        except IndexError:
            return ""

    def get_mediawiki_normal_catlinks(self):
        try:
            mediawiki_normal_catlinks = self.tree.findall(".//div[@id='mw-normal-catlinks']")[0]
            mediawiki_normal_catlinks = etree.tostring(mediawiki_normal_catlinks).decode("utf-8")
            return sub(r"<!--.*?-->", "", mediawiki_normal_catlinks, flags=S)
        except IndexError:
            return ""

    def get_mediawiki_parser_output_and_normal_catlinks(self):
        return self.get_mediawiki_parser_output() + "\n" + self.get_mediawiki_normal_catlinks()

    def get_references(self):
        mediawiki_parser_output = etree.HTML(self.get_mediawiki_parser_output())
        try:
            return mediawiki_parser_output.findall(".//ol[@class='references']/li")
        except:
            return []

    def get_links_in_parser_output(self):
        mediawiki_parser_output = etree.HTML(self.get_mediawiki_parser_output())
        try:
            return mediawiki_parser_output.findall(".//p//a")
        except IndexError:
            return []

    def open_in_firefox(self):

        system("firefox '" + self.url + "'")

        filename = self.title + ".html"
        
        self.save_to_file()

        system("firefox " + filename)

        sleep(0.5)

        remove(filename)

    def save_to_file(self):

        filename = self.title + ".html"

        with open(filename, "w") as file:
            file.write(self.get_mediawiki_parser_output_and_normal_catlinks())

if __name__ == "__main__":

    revisions = {"CRISPR_de_first_rev":"https://de.wikipedia.org/w/index.php?title=CRISPR&oldid=69137443",
                 "CRISPR_en_first_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=17918488",
                 "CRISPR_en_remov_rev":"https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=898138824"}

    page = Page("CRISPR_de_first_rev", revisions["CRISPR_de_first_rev"])
    links_in_parser_output = page.get_links_in_parser_output()
    for link in links_in_parser_output:
        print(link.text)
    references = page.get_references()
    for reference in references:
        print(reference[1][0].text)
