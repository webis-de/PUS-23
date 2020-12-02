from re import sub

class Section:

    def __init__(self, source):

        self.source = source

    def get_text(self):
        """
        Get the full text of the section.

        Returns:
            The full section as a string.
        """
        return sub(r" +", " ", " ".join(self.source.xpath(".//text()")))

    def get_backlink(self, backlink):
        """
        Return all backlings in the section.

        Returns:
            A list of backlinks as strings.
        """
        try:
            return self.source.xpath(".//span[@class='mw-cite-backlink']//a")[0].get("href")[1:]
        except IndexError:
            return None
