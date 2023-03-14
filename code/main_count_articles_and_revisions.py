from wikidump.wikipedia_dump_reader import WikipediaDumpReader
import csv
import logging

from datetime import datetime
from os.path import basename, exists, getsize, sep
from os import environ
from os import makedirs
from glob import glob
from socket import gethostname

#################################################################
# This file serves as an entry point to analyse Wikipedia dumps.#
#################################################################


def get_logger(filename):
    """Set up the logger."""
    logger = logging.getLogger("dump_logger")
    formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%F %H:%M:%S")
    logger.setLevel(logging.DEBUG)
    logging_file_handler = logging.FileHandler(filename, "a")
    logging_file_handler.setFormatter(formatter)
    logging_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(logging_file_handler)
    return logger, logging_file_handler


def log_handler_host(output_directory, hostname, nodename, input_filepath_index, input_filepath, filesize):
    with open(output_directory + sep + hostname + ".txt", "a") as file:
        file.write(str(input_filepath_index).rjust(3, "0") + " " + basename(
            input_filepath) + " " + nodename + " " + str(filesize / (1024**2)) + "\n")


def analyse_dump(input_filepath,
                 output_directory,
                 done_input_filepaths):
    """
    Analyse dump file and log all article titles and page IDs.

    Args:
        input_filepath: Path to dump BZ2 file.
        output_directory: Directory to which log and results are saved.
        done_input_filepaths: Path to file listing completely handled dump files.
    """
    output_file_prefix = output_directory + sep + \
        basename(input_filepath).split(".bz2")[0]
    csv_filepath = output_file_prefix + "_results.csv"
    log_filepath = output_file_prefix + "_log.txt"
    # Check completed input files
    if basename(input_filepath) in done_input_filepaths:
        with open(output_directory + sep + "done_update.txt", "a") as update_file:
            update_file.write("Analysis of file " +
                              basename(input_filepath) + " already complete.\n")
        return
    # Recover last revision handled in case of aborted analysis
    start_article_count = 0
    start_revision_count = 0
    if exists(log_filepath):
        with open(log_filepath) as file:
            try:
                last_log_line = file.readlines()[-1]
                try:
                    start_article_count = int(
                        last_log_line.split(",")[0].strip().split(" >>> ")[-1])
                    start_revision_count = int(
                        last_log_line.split(",")[-1].strip())
                except ValueError:
                    pass
            except IndexError:
                pass

        with open(output_directory + sep + "done_update.txt", "a") as update_file:
            update_file.write("Analysis of file " + basename(input_filepath) + " already started. " +
                              "Starting from " + str(start_article_count) + " articles" +
                              " and " + str(start_revision_count) + " revisions.\n")
    # Start analysis of dump file
    start = datetime.now()
    logger, logging_file_handler = get_logger(log_filepath)

    revision_count = 0
    article_count = 0
    articles = {}

    with WikipediaDumpReader(input_filepath) as wdr:
        for title, pageid, revid, timestamp, text in wdr.line_iter():
            revision_count += 1

            if start_revision_count and revision_count <= start_revision_count:
                continue

            if title not in articles:
                articles[title] = set()
                article_count += 1
            articles[title].add(pageid)

            if revision_count % 1000 == 0:
                logger.info(str(article_count) + "," + str(revision_count))

            if article_count % 1000 == 0:
                with open(csv_filepath, "w", newline="") as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=",")
                    for article_title, page_ids in articles.items():
                        csv_writer.writerow(
                            [article_title, "|".join(page_ids)])
    logger.info(str(article_count) + "," + str(revision_count))
    with open(csv_filepath, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        for article_title, page_ids in articles.items():
            csv_writer.writerow([article_title, "|".join(page_ids)])
    end = datetime.now()
    duration = end - start
    logger.info(duration)
    logging_file_handler.close()
    logger.removeHandler(logging_file_handler)
    with open(output_directory + sep + "done.csv", "a", newline="") as done_file:
        done_file_writer = csv.writer(done_file, delimiter=",")
        done_file_writer.writerow([basename(input_filepath),
                                   article_count,
                                   revision_count,
                                   duration])
        done_file.flush()

if __name__ == "__main__":

    #####################################################################################################
    # The below code is used to analyse the wikitext of wikipedia dumps for article and revision counts.#
    #####################################################################################################

    manual = False
    slice_size = 6

    JOB_COMPLETION_INDEX = 0 if manual else int(
        environ.get("JOB_COMPLETION_INDEX"))

    dump_analysis_directory = "../analysis/articles/2022_05_31_article_and_revision_count"
    if not exists(dump_analysis_directory):
        makedirs(dump_analysis_directory)

    # GET DONE BZ2 FILES
    done_filepath = dump_analysis_directory + sep + "done.csv"
    if exists(done_filepath):
        with open(done_filepath) as file:
            done_input_filepaths = [line.split(
                ",")[0] for line in file.readlines()]
    else:
        done_input_filepaths = []

    corpus_path_prefix = "../../../../../corpora/corpora-thirdparty/corpus-wikipedia/wikimedia-history-snapshots/enwiki-20210601/"

    # CHECK ALL BZ2 FILES
    # EXCLUDE 55 GB FILE, HANDLE MANUALLY
    MANUAL_FILE = "enwiki-20210601-pages-meta-history10.xml-p5128920p5137511.bz2"
    if manual:
        input_filepaths = [filename for filename in glob(corpus_path_prefix + "*.bz2")
                           if MANUAL_FILE in filename]
    else:
        input_filepaths = [filename for filename in glob(corpus_path_prefix + "*.bz2")
                           if not MANUAL_FILE in filename]

    for input_filepath_index, input_filepath in enumerate(input_filepaths[JOB_COMPLETION_INDEX*slice_size:(JOB_COMPLETION_INDEX+1)*slice_size],
                                                          JOB_COMPLETION_INDEX*slice_size):
        filesize = getsize(input_filepath)
        hostname = "dump-pod-jupyter" if manual else gethostname()
        log_handler_host(dump_analysis_directory, hostname, "jupyter-kircheis" if manual else environ.get(
            "NODE_NAME"), input_filepath_index, input_filepath, filesize)

        analyse_dump(input_filepath=input_filepath,
                     output_directory=dump_analysis_directory,
                     done_input_filepaths=done_input_filepaths)
