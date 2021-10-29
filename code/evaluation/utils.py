from urllib.parse import quote, unquote
from os.path import basename

directory = "../../analysis/bibliography/2021_04_02/publication-events/"
JSON = directory + "CRISPR_en.json"
JSON_ANNOTATED = directory + "CRISPR_en_annotated.json"
JSON_CORRECT = directory + "CRISPR_en_correct.json"
JSON_REDUCED = directory + "CRISPR_en_reduced.json"

def parse_json_name(json_path):
    return basename(json_path).split(".")[0]

def parse_article_title(json_name):
    return unquote(json_name).replace("_"," ")
