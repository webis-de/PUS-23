from requests import get as GET
from lxml import html
from re import sub, S
from json import dumps, loads
from os.path import exists, sep
from os import makedirs
from urllib.parse import quote, unquote
from time import sleep
from random import randint, random

class Scraper:
    """
    Scrape revision history from Wikipedia page.

    Attributes:
        logger: The logger this Scraper uses.
        headers: Header for GET request.
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
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
        self.title = title.replace(" ", "_")
        self.language= language
        self.filename = quote(self.title, safe="") + "_" + self.language
        self.api_url = "https://" + language + ".wikipedia.org/w/api.php"
        self.page_id = list(GET(self.api_url, params={"format":"json","action":"query","titles":title}, headers=self.headers).json()["query"]["pages"].keys())[0]
        self.article_url = "https://" + language + ".wikipedia.org/w/index.php?title=" + title
        self.rvprops = "comment|content|contentmodel|flagged|flags|ids|oresscores|parsedcomment|roles|sha1|size|slotsha1|slotsize|tags|timestamp|user|userid"
        self.parameters = {"format":"json","action":"query","titles":title,"prop":"revisions","rvlimit":"50","rvdir":"newer","rvslots":"*","rvprop":self.rvprops}
        self.rvcontinue = None
        self.revision_count = 0
        self.updating = False
        self.update_count = 0

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        pass

    def scrape(self, directory, number = float("inf")):
        """
        Scrape revisions from Wikipedia page.
        Revisions are scraped in batches of a maximum of 50 at a time.

        Args:
            directory: The directory to which the scraped revisions are saved.
            number: Number of revisions to scrape.
        """
        revisions = []
        self.logger.start("Scraping " + self.title + " (" + self.language + ").")
        if exists(str(directory) + sep + self.filename):
            self.get_rvstartid(directory + sep + self.filename)
            self.updating = True
        else:
            self.collect_revisions(directory, number) 
        while self.rvcontinue and self.revision_count < number:
            self.collect_revisions(directory, number)

        if self.updating: self.logger.log("Number of updates: " + str(self.update_count))
        self.logger.stop("Done. Number of revisions: " + str(self.revision_count))

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
        response = GET(self.api_url, {"format":"json","action":"query","titles":self.title,"prop":"revisions","rvlimit":"1","rvdir":"newer","rvstartid":str(latest_revid)}).json()
        self.rvcontinue = response.get("continue",{}).get("rvcontinue",None)
        if self.rvcontinue:
            self.parameters["rvstartid"] = self.rvcontinue.split("|")[1]

    def collect_revisions(self, directory, number):
        """
        Collect all revisions for the Wikipedia article.
        Revisions are scraped in batches of a maximum of 50 at a time.

        Args:
            directory: The directory to which the scraped revisions are saved.
            number: Number of revisions to scrape.
        """
        response = GET(self.api_url, params=self.parameters, headers=self.headers)
        #print(response.status_code)
        response_json = response.json()
        sleep(self.delay())
        for revision in response_json["query"]["pages"][self.page_id]["revisions"]:
            if self.revision_count >= number: break
            revision_url = self.article_url + "&oldid=" + str(revision["revid"])
            self.save(directory,
                      {"revid":revision["revid"],
                       "parentid":revision["parentid"],
                       "url":revision_url,
                       "user":revision["user"],
                       "userid":revision["userid"],
                       "timestamp":revision["timestamp"],
                       "size":revision["size"],
                       "html":self.download_html(revision_url),
                       "comment":revision.get("comment",""),
                       "minor":revision.get("minor",""),
                       "index":self.revision_count})
            self.revision_count += 1
            if self.updating: self.update_count += 1
            if self.revision_count % 100 == 0:
                self.logger.end_check(self.revision_count)
            else:
                print(self.revision_count)
            
        
        
        
        self.rvcontinue = response_json.get("continue",{}).get("rvcontinue",None)
        if self.rvcontinue:
            self.parameters["rvstartid"] = self.rvcontinue.split("|")[1]

    def delay(self):
        """
        Request delay between 2 and 4 seconds.
        
        Returns:
            Float between 2 and 4.
        """
        return 2 + randint(0,1) + random()

    def download_html(self, revision_url):
        """
        Download HTML for a given revision URL.

        Args:
            revision: The URL of the revision for which to obtain HTML.

        Returns:
            The HTML of the revision.
        """
        response = GET(revision_url, headers=self.headers)
        #print(response.status_code)
        tree = html.fromstring(response.text)
        #get text from MediaWiki
        try:
            mediawiki_parser_output = tree.xpath(".//div[@class='mw-parser-output']")[0]
            mediawiki_parser_output = html.tostring(mediawiki_parser_output).decode("utf-8")
            mediawiki_parser_output = sub(r"<!--.*?-->", "", mediawiki_parser_output, flags=S)
        except IndexError:
            mediawiki_parser_output = ""
        #get categories from MediaWiki
        try:
            mediawiki_normal_catlinks = tree.xpath(".//div[@id='mw-normal-catlinks']")[0]
            mediawiki_normal_catlinks = html.tostring(mediawiki_normal_catlinks).decode("utf-8")
            mediawiki_normal_catlinks = sub(r"<!--.*?-->", "", mediawiki_normal_catlinks, flags=S)
        except IndexError:
            mediawiki_normal_catlinks = ""
        HTML = mediawiki_parser_output + "\n" + mediawiki_normal_catlinks
        if not HTML:
            self.logger.log("Issue encountered with revid: " + str(revision["revid"]))        
        sleep(self.delay())
        return HTML
    
    def save(self, directory, revision):
        """
        Save revision to directory.

        Args:
            directory: The directory to which the scraped revision is saved.
            revision: A revision to save to file.
        """
        if not exists(directory): makedirs(directory)
        with open(directory + sep + self.filename, "a") as output_file:
            output_file.write(dumps(revision) + "\n")

