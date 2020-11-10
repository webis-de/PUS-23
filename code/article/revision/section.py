from re import sub

class Section:

    def __init__(self, source):

        self.source = source

    def get_text(self):
        return sub(r" +", " ", " ".join(self.source.xpath(".//text()")))

    def get_backlink(self, backlink):
        try:
            return self.source.xpath(".//span[@class='mw-cite-backlink']//a")[0].get("href")[1:]
        except IndexError:
            return None
