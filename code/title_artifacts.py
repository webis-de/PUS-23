from article.article import Article
from unicodedata import normalize
from glob import glob
from json import load
from pprint import pformat

def to_ascii(string):
    return normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

def to_lower(string):
    return string.lower()

def to_alnum(string):
    return "".join([character for character in string if character.isalnum() or character in [" "]])

def formats(string):
    return to_alnum(to_ascii(to_lower(string)))

jsons = glob("../analysis/bibliography/2021_11_03_analysed/*/*.json")

jsons = [json for json in jsons if not any(["correct" in json,
                                            "annotated" in json,
                                            "reduced" in json])]

jsons = sorted(jsons)

with open("title_artifacts.txt", "w") as error_file:
    for json in jsons:
        with open(json) as file:
            results = load(file)
        article_name = json.split("/")[-1].replace(".json", "") + "_en"
        article_title = list(results[0]["trace"].keys())[0]
        art = Article("../articles/2021-06-01_with_html/en/" + article_name)
        print(json)
        for index, result in enumerate(results):
            wos_key = result["wos_keys"]
            title = result["titles"][wos_key]
            if result["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]:
                if not result["trace"][article_title]["first_mentioned"]["verbatim"]["dois"] or \
                   (result["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]["index"] != \
                    result["trace"][article_title]["first_mentioned"]["verbatim"]["dois"]["index"]):
                        rev = art.get_revision(result["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]["index"])
                        if title not in rev.get_text():
                            error_file.write(json)
                            error_file.write("\n\n")
                            error_file.write(title)
                            error_file.write("\n\n")
                            error_file.write(pformat(result["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]))
                            error_file.write("\n")
                            error_file.write("======================================\n")
                            error_file.flush()
