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

    def get_hrefs(self):
        """
        Return all hrefs in the section.

        Returns:
            A list of hrefs as strings.
        """
        return [element.get("href") for element in self.source.xpath(".//a")]
