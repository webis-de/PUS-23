from utility.utils import lzma_and_remove
from utility.logger import Logger
from revision import Revision
from requests import get
from json import dump, load
from os.path import exists, sep
from os import makedirs
from multiprocessing import Pool

class Scraper:
    """
    Scrape revision history from Wikipedia page.

    Attributes:
        title: The title of the Wikipedia page.
        language: he language of the Wikipedia page.
        api_url: URL of Wikimedia API as per language.
        parameters: Parameters for the get request to the Wikipedia REST API.
        page_id: ID of the Wikipedia page.
        revisions: Deserialised revisions of this Wikipedia page.
        revision_count: The number of revisions of this Wikipedia page.
    """
    def __init__(self, logger, title, language):
        """
        Initialise scraper.

        Args:
            title: The title of the Wikipedia page to scrape.
            language: The language of the Wikipedia page to scrape.
        """
        self.logger = logger
        self.title = title
        self.language= language
        self.api_url = "https://" + language + ".wikipedia.org/w/api.php"
        self.article_url = "https://" + language + ".wikipedia.org/w/index.php?title=" + title
        rvprops = "comment|content|contentmodel|flagged|flags|ids|oresscores|parsedcomment|roles|sha1|size|slotsha1|slotsize|tags|timestamp|user|userid"
        self.parameters = {"format":"json","action":"query","prop":"revisions","titles":title,"rvlimit":"50","rvdir":"newer","rvslots":"*","rvprop":rvprops}
        self.page_id = None
        self.revisions = []
        self.revision_count = 0

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        """Closes the log when the resource this API uses is closed."""
        pass

    def scrape(self, html = True):
        """Scrape the Wikipedia page."""
        self.logger.start_check("Scraping " + self.title)
        response = get(self.api_url, self.parameters).json()
        self.page_id = list(response["query"]["pages"].keys())[0]
        self.collect_revisions(response) 
        while self.parameters["rvcontinue"]:
            self.collect_revisions(get(self.api_url, self.parameters).json())
        if html:
            pool = Pool()
            self.revisions = pool.map(self.html, self.revisions)
            pool.close()
            pool.join()
        self.logger.end_check("Done. Number of revisions: " + str(self.revision_count))

    def html(self, revision):
        revision.get_html()
        return revision

    def collect_revisions(self, response):
        """
        Collect the revisions in the response.

        Args:
            response: The response of the Wikipedia REST API.
        """
        for revision in response["query"]["pages"][self.page_id]["revisions"]:
            self.revisions.append(Revision(revision["revid"],
                                      revision["parentid"],
                                      self.article_url + "&oldid=" + str(revision["revid"]),
                                      revision["user"],
                                      revision["userid"],
                                      revision["timestamp"],
                                      revision["size"],
                                      revision.get("slots",{}).get("main",{}).get("*",""),
                                      "",
                                      revision.get("comment",""),
                                      revision.get("minor",""),
                                      self.revision_count))
            self.revision_count += 1
        self.parameters["rvcontinue"] = response.get("continue",{}).get("rvcontinue",None)
    
    def save(self, directory, compress = False):
        """
        Save revisions to directory.

        Args:
            directory: The directory to save the scraped revision history to.
            compress: Compress file using lzma and delete json if set to True.
        """
        if not exists(directory): makedirs(directory)
        title = self.title.replace("/","-")
        with open(directory + sep + title + "_" + self.language + ".json", "w") as output_file:
            for revision in self.revisions:
                dump(revision.__dict__, output_file)
                output_file.write("\n")
        if compress:
            lzma_and_remove(directory + sep + title + "_" + self.language + ".json",
                            directory + sep + title + "_" + self.language + ".json.xz")

if __name__ == "__main__":
    logger = Logger()
    
    with open("../data/wikipedia_articles.json") as articles_file:
        wikipedia_articles = load(articles_file)

    articles = [article for values in wikipedia_articles.values() for article in values]

    logger.start("Scraping " + ", ".join(articles))
    for article in articles[1:]:
        with Scraper(logger = logger, title = article, language = "en") as scraper:
            scraper.scrape(html = False)
            scraper.save(directory = "../extractions", compress = True)
    logger.stop("Done.")
    logger.close()

