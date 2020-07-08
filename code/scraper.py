from revision import Revision
from requests import get
from utils import lzma_and_remove
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
        parameters: Parameters of the get request to the Wikipedia REST API.
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
        self.parameters = {"format":"json","action":"query","prop":"revisions","titles":title,"rvlimit":"50","rvdir":"newer","rvslots":"*","rvprop":"ids|timestamp|user|userid|size|comment|content"}
        self.title = title
        self.language= language
        self.revisions = []

    def scrape(self):
        """Scrape the Wikipedia page and collect revisions."""
        index = 0
        response = get(self.url, self.parameters).json()
        page_id = list(response["query"]["pages"].keys())[0]
        while True:            
            for revision in response["query"]["pages"][page_id]["revisions"]:
                self.revisions.append(Revision(revision["revid"],
                                               revision["user"],
                                               revision["userid"],
                                               revision["timestamp"],
                                               revision["size"],
                                               revision.get("slots",{}).get("main",{}).get("*",""),
                                               revision["comment"],
                                               index))
                index += 1
            self.parameters["rvcontinue"] = response.get("continue",{}).get("rvcontinue",None)
            if not self.parameters["rvcontinue"]:
                break
            response = get(self.url, self.parameters).json()

    def save(self, directory, compress = False):
        """
        Save revisions to directory.

        Args:
            directory: The directory to save the scraped revision history to.
            compress: Compress file using lzma and delete json if set to True.
        """
        if not exists(directory): makedirs(directory)
        with open(directory + sep + self.title + "_" + self.language + ".json", "w") as output_file:
            for revision in self.revisions:
                dump(revision.__dict__, output_file)
                output_file.write("\n")
        if compress:
            lzma_and_remove(directory + sep + self.title + "_" + self.language + ".json",
                            directory + sep + self.title + "_" + self.language + ".json.xz")

if __name__ == "__main__":
    article = Scraper("CRISPR", "de")
    article.scrape()
    #article.save("../data", True)

