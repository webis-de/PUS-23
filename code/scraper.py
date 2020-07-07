from revision import Revision
from requests import get
from json import dump
from os.path import exists, sep
from os import makedirs

class Scraper:
    """
    Scrape revision history from Wikipedia page.

    Attributes:
        url: URL of the Wikipedia article.
        parameters: Parameters for the get request.
        title: The title of the Wikipedia page.
        language: he language of the Wikipedia page.
        page_id: ID of the Wikipedia page.
        current_revision: The latest revision of the Wikipedia article.
        revisions: Deserialised revisions of this Wikipedia page.
    """

    def __init__(self, title, language):
        """
        Initialise scraper.

        Args:
            title: The title of the Wikipedia page to scrape.
            language: The language of the Wikipedia page to scrape.
        """

        self.url = "https://" + language + ".wikipedia.org/w/api.php"
        self.parameters = {"format":"json","action":"query","prop":"revisions","titles":title,"rvlimit":"1","rvdir":"newer","rvslots":"*","rvprop":"content|ids|timestamp"}
        self.title = title
        self.language= language
        current_revision = get(self.url, self.parameters).json()
        
        self.page_id = list(current_revision["query"]["pages"].keys())[0]
        self.parameters["rvcontinue"] = current_revision["continue"]["rvcontinue"]

        current_revision = current_revision["query"]["pages"][self.page_id]["revisions"][0]
        self.current_revision = Revision(current_revision["revid"],current_revision.get("slots",{}).get("main",{}).get("*",""),current_revision["timestamp"], 0)
        
        self.revisions = [self.current_revision]

    def scrape(self):
        """Scrape the Wikipedia page and collect revisions."""
        self.parameters["rvlimit"] = "50"
        index = 1
        while self.parameters["rvcontinue"]:            
            response = get(self.url, self.parameters).json()
            self.parameters["rvcontinue"] = response.get("continue",{}).get("rvcontinue",None)
            for revision in response["query"]["pages"][self.page_id]["revisions"]:
                self.revisions.append(Revision(revision["revid"],revision.get("slots",{}).get("main",{}).get("*",""),revision["timestamp"], index))
                index += 1
        for index in range(len(self.revisions)):
            self.revisions[index].index = index

    def save(self, directory):
        """
        Save revisions to directory.

        Args:
            The directory to save the scraped revision history to.
        """
        if not exists(directory): makedirs(directory)
        with open(directory + sep + self.title + "_" + self.language + ".json", "w") as output_file:
            for revision in self.revisions:
                dump({"id":revision.id,"text":{"#text":revision.text},"timestamp":revision.timestamp}, output_file)
                output_file.write("\n")

if __name__ == "__main__":
    article = Scraper("CRISPR", "en")
    article.scrape()
    article.save("../data")

