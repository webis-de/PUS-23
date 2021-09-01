from utility.wikipedia_dump_reader import WikipediaDumpReader
from lxml.etree import ElementTree
import bz2
from datetime import datetime
from pyspark.sql import SparkSession

input_filepath = "wikipedia_dump.bz2" #500kb

#xml parsing
start = datetime.now()
revision_count = 0

with bz2.open(input_filepath, "rt") as bz2file:
    root = ElementTree().parse(bz2file)
    for page in root.findall("page", ns):
        if page.find("ns", ns).text == "0":
            for revision in page.findall("revision", ns):
                revision_count += 1

print(revision_count, datetime.now() - start)

#lineparsing
start = datetime.now()
revision_count = 0

with bz2.open(input_filepath, "rt") as bz2file:
    readrevision = False
    for line in bz2file:
        if "<ns>" in line:
            readrevision = "<ns>0</ns>" in line
        if "<revision>" in line and readrevision:
            revision_count += 1

print(revision_count, datetime.now() - start)

#iterative xml parsing
start = datetime.now()
revision_count = 0

with WikipediaDumpReader(input_filepath) as wdr:
    for revision in wdr:
        revision_count += 1

print(revision_count, datetime.now() - start)

