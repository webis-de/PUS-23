from entity.article import Article
from entity.revision import Revision
from requests import get
from json import dumps, loads
from os.path import exists, sep
from os import makedirs
from multiprocessing import Pool

class Scraper:
    """
    Scrape revision history from Wikipedia page.

    Attributes:
        logger: The logger this Scraper uses.
        title: The title of the Wikipedia page.
        language: The language of the Wikipedia article.
        filename: The name of the file under which the revisions will be saved,
                  which is a concatenation of <title>_<language>
                  To avoid path issues, '/' is replaced with '-'.
        api_url: The URL of Wikimedia API as per language.
        page_id: ID of the Wikipedia page.
        article_url: The URL of the Wikipedia article.
        rvprops: The revision properties that will be requested from the REST API.
        parameters: Parameters for the get request to the Wikipedia REST API.
        rvcontinue: Concatenation of timestamp, pipe (|) and revid of the next revision,
                    if available; else None.
        revision_count: The number of revisions extracted by this Scraper.
        updating: Flag for update mode.
        update_count: Number of revisions scraped if updating.
        revisions: Deserialised revisions of this Wikipedia page.
    """
    def __init__(self, logger, title, language):
        """
        Initialise scraper.

        Args:
            logger: The logger this Scraper uses.
            title: The title of the Wikipedia page to scrape.
            language: The language of the Wikipedia page to scrape.
        """
        self.logger = logger
        self.title = title
        self.language= language
        self.filename = self.title.replace("/","-") + "_" + self.language
        self.api_url = "https://" + language + ".wikipedia.org/w/api.php"
        self.page_id = list(get(self.api_url, {"format":"json","action":"query","titles":title}).json()["query"]["pages"].keys())[0]
        self.article_url = "https://" + language + ".wikipedia.org/w/index.php?title=" + title
        self.rvprops = "comment|content|contentmodel|flagged|flags|ids|oresscores|parsedcomment|roles|sha1|size|slotsha1|slotsize|tags|timestamp|user|userid"
        self.parameters = {"format":"json","action":"query","titles":title,"prop":"revisions","rvlimit":"50","rvdir":"newer","rvslots":"*","rvprop":self.rvprops}
        self.rvcontinue = None
        self.revision_count = 0
        self.updating = False
        self.update_count = 0

        self.revisions = []

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        pass

    def scrape(self, directory, html = True, number = float("inf")):
        """
        Scrape the Wikipedia page.

        Args:
            directory: The directory to which the scraped revisions are saved.
            html: Scrape HTML code of each revision.
            number: Number of revisions to scrape.
        """
        self.logger.start_check("Scraping " + self.title + " (" + self.language + ")" + " and extracting html" * html + ".")
        if exists(directory + sep + self.filename):
            self.get_rvstartid(directory + sep + self.filename)
            self.updating = True
        else:
            self.collect_revisions(directory, html, number) 
        while self.rvcontinue and self.revision_count < number:
            self.collect_revisions(directory, html, number)

        if self.updating: self.logger.log("Number of updates: " + str(self.update_count))
        self.logger.end_check("Done. Number of revisions: " + str(self.revision_count))

    def get_rvstartid(self, filepath):
        """
        Helper function to set up revision update. Opens revision file, obtains last revision id,
        requests revision from API, sets rvcontinue to API value if available (None if not available)
        and extracts start id from rvcontinue value.

        The rvcontinue value is a string of concatinated timestamp, pipe (|) and the revid of the next revision,
        i.e. revision with id 72067857 and timestamp "2010-03-19T00:40:01Z" has a parent with the rvcontinue value
        "20100319004001|72067857".

        Args:
            filepath: Path to the revisions file.
        """
        with open(filepath) as article:
            for line in article:
                self.revision_count += 1
                LINE = line
        latest_revid = loads(LINE)["revid"]
        response = get(self.api_url, {"format":"json","action":"query","titles":self.title,"prop":"revisions","rvlimit":"1","rvdir":"newer","rvstartid":str(latest_revid)}).json()
        self.rvcontinue = response.get("continue",{}).get("rvcontinue",None)
        if self.rvcontinue:
            self.parameters["rvstartid"] = self.rvcontinue.split("|")[1]

    def collect_revisions(self, directory, html, number):
        """
        Collect the revisions in the response.

        Args:
            directory: The directory to which the scraped revisions are saved.
            html: Scrape HTML code of each revision.
            number: Number of revisions to scrape.
        """
        response = get(self.api_url, self.parameters).json()
        self.revisions = []
        for revision in response["query"]["pages"][self.page_id]["revisions"]:
            if self.revision_count >= number: break
            self.revisions.append(Revision(revision["revid"],
                                           revision["parentid"],
                                           self.article_url + "&oldid=" + str(revision["revid"]),
                                           revision["user"],
                                           revision["userid"],
                                           revision["timestamp"],
                                           revision["size"],
                                           "",
                                           revision.get("comment",""),
                                           revision.get("minor",""),
                                           self.revision_count))
            self.revision_count += 1
            if self.updating: self.update_count += 1

        if html: self.revisions = self.collect_html(self.revisions)

        self.save(self.revisions, directory)
        
        self.rvcontinue = response.get("continue",{}).get("rvcontinue",None)
        if self.rvcontinue:
            self.parameters["rvstartid"] = self.rvcontinue.split("|")[1]

    def html(self, revision):
        """
        Helper function to extract HTML for a given revision used during multiprocessing.

        Args:
            revision: The revision to update with HTML.

        Returns:
            The same revision but with updated HTML.
        """
        result = revision.request_html()
        if result: self.logger.log("Issue encountered with revid: " + str(result))
        return revision

    def collect_html(self, revisions):
        """
        Multiprocessing pool retrieval of HTML for revisions.

        Args:
            revisions: List of revisions without HTML.

        Returns:
            List of revisions with HTML.
        """
        pool = Pool(10)
        html_revisions = pool.map(self.html, revisions)
        pool.close()
        pool.join()
        return html_revisions
    
    def save(self, revisions, directory):
        """
        Save revisions to directory.

        Args:
            revisions: A list of revisions to save to file.
            directory: The directory to which the scraped revisions are saved.
        """
        if not exists(directory): makedirs(directory)
        with open(directory + sep + self.filename, "a") as output_file:
            for revision in revisions:
                output_file.write(dumps(revision.__dict__) + "\n")

