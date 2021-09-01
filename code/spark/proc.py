import bz2
from xml.etree import ElementTree
import pyarrow.parquet as pq
import pyarrow as pa
from re import findall

def process(input_filepath, output_filepath):
    bz2_file = bz2.open(input_filepath, "rb")
    xml_iterator = ElementTree.iterparse(bz2_file)
    revisions = {"title":[],"revid":[],"timestamp":[],"text":[]}
    read_revisions = False
    for event, element in xml_iterator:
        if element.tag.split("}")[-1] == "title":
            title = element.text
        elif element.tag.split("}")[-1] == "ns":
            read_revisions = element.text == "0"
        elif read_revisions:
            if element.tag.split("}")[-1] == "revision":
                for subelement in element:
                    if subelement.tag.split("}")[-1] == "id":
                        revid = subelement.text
                    if subelement.tag.split("}")[-1] == "timestamp":
                        timestamp = subelement.text
                    if subelement.tag.split("}")[-1] == "text":
                        text = subelement.text
                revisions["title"].append(title)
                revisions["revid"].append(revid)
                revisions["timestamp"].append(timestamp)
                revisions["text"].append(text)
                element.clear()
        else:
            element.clear()
    table = pa.Table.from_pydict(revisions)
    pq.write_table(table, output_filepath)

process("wikipedia_dump.bz2","wikipedia_dump.parquet")
