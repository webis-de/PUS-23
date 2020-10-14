class Reference:

    def __init__(self, source, number):

        self.source = source
        self.number = number

    def text(self):
        try:
            return "".join(self.source.xpath(".//cite")[0].itertext())
        except IndexError:
            return  "".join(self.source.itertext())

    def backlinks(self):
        return [backlink.get("href")[1:] for backlink in self.source.xpath(".//span[@class='mw-cite-backlink']//a")]

    def linked_sections(self, paragraphs):
        linked_paragraphs = set()
        for paragraph in paragraphs:
            backlinks = self.backlinks()
            if backlinks and paragraph.source.xpath("|".join([".//sup[@id='" + backlink + "']" for backlink in backlinks])):
                linked_paragraphs.add(paragraph)
        return linked_paragraphs
