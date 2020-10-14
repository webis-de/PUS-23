from re import sub

class Paragraph:

    def __init__(self, source):

        self.source = source

    def text(self):
        return sub(r" +", " ", " ".join(self.source.xpath(".//text()")))

    def backlink(self, backlink):
        try:
            return self.source.xpath(".//span[@class='mw-cite-backlink']//a")[0].get("href")[1:]
        except IndexError:
            return None
