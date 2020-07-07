from requests import get
from json import dump
from os.path import exists, sep
from os import makedirs

class Scraper:
    """
    Scrape revision history from Wikipedia page.

    Attributes:
        url: url of the Wikipedia article.
        title: The title of the Wikipedia page.
        language: he language of the Wikipedia page.
        page_id: ID of the Wikipedia page.
        rv_continue: Holds value of starting ID of next batch to scrape.
        revisions: Revisions of this Wikipedia page.
    """

    def __init__(self, title, language):
        """
        Initialise scraper.

        Args:
            title: The title of the Wikipedia page to scrape.
            language: The language of the Wikipedia page to scrape.
        """

        self.url = "https://" + language + ".wikipedia.org/w/api.php?format=json&action=query&prop=revisions&titles=" + title + "&rvlimit=1&&rvslots=*&rvprop=content|ids|timestamp"
        self.title = title
        self.language= language
        current_revision = get(self.url).json()
        
        self.page_id = list(current_revision["query"]["pages"].keys())[0]
        self.rv_continue = current_revision["continue"]["rvcontinue"]

        current_revision = current_revision["query"]["pages"][self.page_id]["revisions"][0]
        rev_id = current_revision["revid"]
        rev_text = current_revision["slots"]["main"]["*"]
        rev_timestamp = current_revision["timestamp"]
        
        self.revisions = [{"id":rev_id,"text":rev_text,"timestamp":rev_timestamp}]

    def scrape(self):
        """Scrape the Wikipedia page and collect revisions."""        
        while self.rv_continue:
            url = "https://" + self.language + ".wikipedia.org/w/api.php?format=json&action=query&prop=revisions&titles=" + self.title + "&rvlimit=50&rvslots=*&rvprop=content|ids|timestamp&rvcontinue=" + self.rv_continue
            response = get(url).json()
            try:
                self.rv_continue = response["continue"]["rvcontinue"]
            except:
                self.rv_continue = ""
            for revision in response["query"]["pages"][self.page_id]["revisions"]:
                rev_id = revision["revid"]
                try:
                    rev_text = revision["slots"]["main"]["*"]
                except:
                    rev_text = ""
                rev_timestamp = revision["timestamp"]
                self.revisions.append({"id":rev_id,"text":rev_text,"timestamp":rev_timestamp})
            print(len(self.revisions))

    def save(self, directory):
        """
        Save revisions to directory.

        Args:
            The directory to save the scraped revision history to.
        """
        if not exists(directory): makedirs(directory)
        with open(directory + sep + self.title + "_" + self.language + ".json", "w") as output_file:
            for revision in self.revisions[::-1]:
                dump({"id":revision["id"],"text":{"#text":revision["text"]},"timestamp":revision["timestamp"]}, output_file)
                output_file.write("\n")

if __name__ == "__main__":
    article = Scraper("CRISPR", "de")
    article.scrape()
    article.save("../data")

