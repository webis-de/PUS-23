from requests import get as GET
from lxml import html
from re import sub, S
from json import dumps, loads
from os.path import exists, sep
from os import makedirs
from urllib.parse import quote, unquote
from time import sleep
from random import randint, random
from datetime import datetime
import logging

class Scraper:
    """
    Scrape revision history from Wikipedia page.

    Attributes:
        directory: The directory to which scraped revisions will be saved.
        logger: The logger this Scraper uses.
        headers: Header for GET request.
        title: The title of the Wikipedia page.
        language: The language of the Wikipedia article.
        filename: The name of the file under which the revisions will be saved,
                  which is a concatenation of <title>_<language>
                  The title is automatically formated to avoid path issues.
        api_url: The URL of Wikimedia API as per language.
        page_id: ID of the Wikipedia page.
        article_url: The URL of the Wikipedia article.
        parameters: Parameters for the get request to the Wikipedia REST API.
        rvcontinue: Concatenation of timestamp, pipe (|) and revid of the next revision,
                    if available; else None.
        revision_count: The number of revisions extracted by this Scraper.
        updating: Flag for update mode.
        update_count: Number of revisions scraped if updating.
    """
    def __init__(self, directory, title, language):
        """
        Initialise scraper.

        Args:
            directory: The directory to which scraped revisions will be saved.
            title: The title of the Wikipedia page to scrape.
            language: The language of the Wikipedia page to scrape.
        """
        self.directory = directory
        if not exists(directory): makedirs(directory)
        self.logger = self._logger(directory)
        self.headers = {'user-agent': 'Modzilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
        self.language = language
        self.api_url = "https://" + language + ".wikipedia.org/w/api.php"
        self.page_id = None
        self.title = self._sanity_check(title)
        self.filename = self._quote_filename(self.title)
        self.article_url = "https://" + language + ".wikipedia.org/w/index.php?title=" + self.title
        self.parameters = {"format":"json","action":"query","titles":self.title,"prop":"revisions","rvlimit":"50","rvdir":"newer","rvslots":"*",
                           "rvprop":"comment|content|contentmodel|flagged|flags|ids|oresscores|parsedcomment|roles|sha1|size|slotsha1|slotsize|tags|timestamp|user|userid"}
        self.rvcontinue = None
        self.revision_count = 0
        self.updating = False
        self.update_count = 0

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        """Logs the number of scraped and updated revisions when the instance is closed."""
        if self.updating: self.logger.info("Number of updates: " + str(self.update_count))
        self.logger.info("Done. Number of revisions: " + str(self.revision_count))

    def _logger(self, directory):
        """Set up the logger for this scraper."""
        logger = logging.getLogger("scraper_logger")
        formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%F %H:%M:%S")
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        file_handler = logging.FileHandler(self.directory + sep + "log.txt", "a")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        return logger

    def _quote_filename(self, title):
        """
        Replace blanks with underscore and quote reserved path separators like '/'.

        Args:
            title: The title of the article.
        Returns:
            The title as a quoted filename.
        """
        return quote(title.replace(" ", "_"), safe="") + "_" + self.language

    def _unquote_filename(self, filename):
        """
        Unquotes the filename to return the title of the article.

        Args:
            title: The title of the article.
        Returns:
            The title as a quoted filename.
        """
        return " ".join(unquote(filename).split("_")[:-1])

    def _sanity_check(self, title):
        """
        Check article for redirect and reset title if applicable.

        Args:
            title: The title of the page to check.
        Returns:
            The corrected titles as defined by the redirect.
        """
        response = GET(self.api_url, params={"format":"json","action":"query","titles":title,"redirects":""}, headers=self.headers, timeout=5).json()
        self.page_id = list(response["query"]["pages"].keys())[0]
        if self.page_id == "-1":
            self.logger.warning("Article '" + title + "' does not exist.")
        redirect = response["query"].get("redirects", [{"to":None}])[0]["to"]
        if redirect:
            self.logger.warning("Article '" + title + "' redirects to " + redirect + ". Setting title to " + redirect + ".")
            return redirect
        else:
            return title

    def scrape(self, directory, deadline, number = float("inf"), verbose = True, gethtml = True):
        """
        Scrape revisions from Wikipedia page.
        Revisions are scraped in batches of a maximum of 50 at a time.

        Args:
            directory: The directory to which the scraped revisions are saved.
            deadline: The deadline before which collections are collected. Use 'YYYY-MM-DD'.
            number: Number of revisions to scrape.
            verbose: Print revision count progress.
            gethtml: Download HTML of revision.
        """
        if self.page_id == "-1":
            return 1
        else:
            revisions = []
            self.logger.info("Scraping revisions of " + self.title + " (" + self.language + ") before " + deadline + ".")
            if not gethtml: self.logger.info("Not getting HTLM.")
            if exists(str(directory) + sep + self.filename):
                self._rvstartid(directory + sep + self.filename)
                self.updating = True
            else:
                self.rvcontinue = True
            while self._collect_revisions(directory, deadline, number, verbose, gethtml):
                pass
            return 0

    def _rvstartid(self, filepath):
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
        latest_revid = self._latest_revid(filepath)
        response = GET(self.api_url, {"format":"json","action":"query","titles":self.title,"prop":"revisions","rvlimit":"1","rvdir":"newer","rvstartid":str(latest_revid)}, timeout=5).json()
        self.rvcontinue = response.get("continue",{}).get("rvcontinue",None)
        if self.rvcontinue:
            self.parameters["rvstartid"] = self.rvcontinue.split("|")[1]

    def _latest_revid(self, filepath):
        """
        Get the latest revision id from a revision dump, i.e. the id of the last entry line.

        Args:
            filepath: Path to the revisions file.
        Returns:
            The the latest revision id in the revision dump.
        """
        with open(filepath) as article:
            for line in article:
                self.revision_count += 1
                LINE = line
        return loads(LINE)["revid"]

    def _collect_revisions(self, directory, deadline, number, verbose, gethtml):
        """
        Collect all revisions for the Wikipedia article.
        Revisions are scraped in batches of a maximum of 50 at a time.

        Args:
            directory: The directory to which the scraped revisions are saved.
            deadline: The deadline before which collections are collected. Use 'YYYY-MM-DD'.
            number: Number of revisions to scrape.
            verbose: Print revision count progress.
            gethtml: Download HTML of revision.
        Returns:
            False if maximum number of revision to scrape has been reached, scraped revision
            date is on day of deadline or there are no more revisions, else True.
        """
        if self.rvcontinue:
            response = GET(self.api_url, params=self.parameters, headers=self.headers, timeout=5)
            response_json = response.json()
            sleep(self._delay())
            for revision in response_json["query"]["pages"][self.page_id]["revisions"]:
                if self.revision_count >= number:
                    return False
                if not self._before(revision["timestamp"], deadline):
                    return False
                revision_url = self.article_url + "&oldid=" + str(revision["revid"])
                self._save(directory,
                          {"revid":revision["revid"],
                           "parentid":revision["parentid"],
                           "url":revision_url,
                           "user":revision.get("user", None),
                           "userid":revision.get("userid", None),
                           "timestamp":revision["timestamp"],
                           "size":revision["size"],
                           "wikitext":revision["slots"]["main"].get("*", ""),
                           "html":self._download_html(revision_url) if gethtml else None,
                           "comment":revision.get("comment",""),
                           "minor":revision.get("minor",""),
                           "index":self.revision_count})
                self.revision_count += 1
                if self.updating: self.update_count += 1
                if self.revision_count % 100 == 0:
                    self.logger.info(self.revision_count)
                else:
                    if verbose: print("revision count:",str(self.revision_count).rjust(5, " "),"revid:",revision["revid"])

            self.rvcontinue = response_json.get("continue",{}).get("rvcontinue",None)
            if self.rvcontinue:
                self.parameters["rvstartid"] = self.rvcontinue.split("|")[1]
                return True
            else:
                return False
        else:
            return False

    def _delay(self):
        """
        Request delay between 2 and 4 seconds.
        
        Returns:
            Float between 2 and 4.
        """
        return 2 + randint(0,1) + random()

    def _download_html(self, revision_url):
        """
        Download HTML for a given revision URL.

        Args:
            revision: The URL of the revision for which to obtain HTML.

        Returns:
            The HTML of the revision.
        """
        response = GET(revision_url, headers=self.headers, timeout=5)
        tree = html.fromstring(response.text)
        #get text from MediaWiki
        try:
            mediawiki_parser_output = tree.xpath(".//div[@class='mw-parser-output']")[0]
            mediawiki_parser_output = html.tostring(mediawiki_parser_output).decode("utf-8")
            mediawiki_parser_output = sub(r"<!--.*?-->", "", mediawiki_parser_output, flags=S)
        except IndexError:
            mediawiki_parser_output = "<div class='mw-parser-output'></div>"
        #get categories from MediaWiki
        try:
            mediawiki_normal_catlinks = tree.xpath(".//div[@id='mw-normal-catlinks']")[0]
            mediawiki_normal_catlinks = html.tostring(mediawiki_normal_catlinks).decode("utf-8")
            mediawiki_normal_catlinks = sub(r"<!--.*?-->", "", mediawiki_normal_catlinks, flags=S)
        except IndexError:
            mediawiki_normal_catlinks = "<div id='mw-normal-catlinks' class='mw-normal-catlinks'></div>"
        HTML = mediawiki_parser_output + mediawiki_normal_catlinks
        if not HTML:
            self.logger.warning("Issue encountered with revid: " + str(revision["revid"]))        
        sleep(self._delay())
        return HTML
    
    def _save(self, directory, revision):
        """
        Save revision to directory.

        Args:
            directory: The directory to which the scraped revision is saved.
            revision: A revision to save to file.
        """
        if not exists(directory): makedirs(directory)
        with open(directory + sep + self.filename, "a") as output_file:
            output_file.write(dumps(revision) + "\n")

    def _before(self, timestamp, deadline):
        """
        Determine whether timestamp is before a given deadline.
        Use string with format 'YYYY-MM-DD'.

        Args:
            timestamp: The timestamp to check.
            deadline: The deadline to check against.

        Return:
            True if timestamp is before deadline, else False.
        """
        timestamp = datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ")
        deadline = datetime.strptime(deadline,"%Y-%m-%d")
        if timestamp.year < deadline.year:
            return True
        else:
            if timestamp.year == deadline.year:
                if timestamp.month < deadline.month:
                    return True
                else:
                    if timestamp.month == deadline.month:
                        if timestamp.day < deadline.day:
                            return True
                        else:
                            return False
                    else:
                        return False
            else:
                return False

if __name__ == "__main__":

    wikipedia_api_url = ("https://en.wikipedia.org/w/api.php?format=json&action=query&titles=CRISPR"
                         "&prop=revisions&rvlimit=1&rvdir=newer&rvslots=*&rvstartid=1009355338"
                         "&rvprop=comment|content|contentmodel|flagged|flags|ids|oresscores|parsedcomment|roles|sha1|size|slotsha1|slotsize|tags|timestamp|user|userid")

    from os import popen

    popen("firefox '" + wikipedia_api_url + "'")
