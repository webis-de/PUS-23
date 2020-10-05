from requests import get
from lxml import html
from re import sub, S
from os import remove, system
from time import sleep

class Page:

    def __init__(self, title, url):

        self.title = title
        self.url = url
        self.html = get(self.url).text
        self.tree = html.fromstring(self.html)

    def get_mediawiki_parser_output(self):
        try:
            mediawiki_parser_output = self.tree.xpath(".//div[@class='mw-parser-output']")[0]
            mediawiki_parser_output = html.tostring(mediawiki_parser_output).decode("utf-8")
            return sub(r"<!--.*?-->", "", mediawiki_parser_output, flags=S)
        except IndexError:
            return ""

    def get_mediawiki_normal_catlinks(self):
        try:
            mediawiki_normal_catlinks = self.tree.xpath(".//div[@id='mw-normal-catlinks']")[0]
            mediawiki_normal_catlinks = html.tostring(mediawiki_normal_catlinks).decode("utf-8")
            return sub(r"<!--.*?-->", "", mediawiki_normal_catlinks, flags=S)
        except IndexError:
            return ""

    def get_mediawiki_parser_output_and_normal_catlinks(self):
        return self.get_mediawiki_parser_output() + "\n" + self.get_mediawiki_normal_catlinks()

    def get_text(self):
        try:
            return "".join(self.tree.xpath(".//div[@class='mw-parser-output']")[0].itertext())
        except IndexError:
            return ""

    def get_references(self):
        return self.tree.xpath(".//div[@class='mw-parser-output']//span[@class='reference-text']")

    def get_links_in_parser_output(self):
        return self.tree.xpath(".//div[@class='mw-parser-output']//p/a")

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

    print("LINKS\n")
    links_in_parser_output = page.get_links_in_parser_output()
    print("\n".join([link.text for link in links_in_parser_output]))
    print("="*50)
    
    print("REFERENCES\n")
    references = page.get_references()
    print("\n\n".join(["\n".join([text.strip() for text in reference.itertext()]) for reference in references]))
    print("="*50)
    
    print("TEXT\n")
    print(page.get_text().strip())
    print("="*50)
