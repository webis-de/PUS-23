from code.wikidump.wikitext_reader import WikitextReader
from json import load
import unittest


class TestWikitextReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.input_directory = "tests/data/wikitext_reader/"

    def test_init(self):
        with open(self.input_directory + "Algorithm.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        self.assertEqual(wtr.article_title, "Algorithm")
        self.assertEqual(wtr.pageid, "775")
        self.assertEqual(wtr.revid, "1062001942")
        self.assertEqual(wtr.timestamp, "2021-12-25T14:53:25Z")

    def test_process(self):
        with open(self.input_directory + "Algorithm.json") as file:
            algorithm = load(file)

        wtr = WikitextReader(*algorithm.values())

        headings = [['Algorithm', 1],
                    ['History', 2],
                    ['Informal definition', 2],
                    ['Formalization', 2],
                    ['Expressing algorithms', 2],
                    ['Design', 2],
                    ['Computer algorithms', 2],
                    ['Examples', 2],
                    ['Algorithm example', 3],
                    ["Euclid's algorithm", 3],
                    ["Computer language for Euclid's algorithm", 4],
                    ["An inelegant program for Euclid's algorithm", 4],
                    ["An elegant program for Euclid's algorithm", 4],
                    ['Testing the Euclid algorithms', 3],
                    ['Measuring and improving the Euclid algorithms', 3],
                    ['Algorithmic analysis', 2],
                    ['Formal versus empirical', 3],
                    ['Execution efficiency', 3],
                    ['Classification', 2],
                    ['By implementation', 3],
                    ['By design paradigm', 3],
                    ['Optimization problems', 3],
                    ['By field of study', 3],
                    ['By complexity', 3],
                    ['Continuous algorithms', 3],
                    ['Legal issues', 2],
                    ['History: Development of the notion of "algorithm"', 2],
                    ['Ancient Near East', 3],
                    ['Discrete and distinguishable symbols', 3],
                    ['Manipulation of symbols as "place holders" for numbers: algebra', 3],
                    ['Cryptographic algorithms', 3],
                    ['Mechanical contrivances with discrete states', 3],
                    ['Mathematics during the 19th century up to the mid-20th century', 3],
                    ['Emil Post (1936) and Alan Turing (1936–37, 1939)', 3],
                    ['J.B. Rosser (1939) and S.C. Kleene (1943)', 3],
                    ['History after 1950', 3],
                    ['See also', 2],
                    ['Notes', 2],
                    ['Bibliography', 2],
                    ['Further reading', 2],
                    ['External links', 2]]

        categories = ["algorithms", "articles with example pseudocode",
                      "mathematical logic", "theoretical computer science"]

        extracted_headings, extracted_categories = wtr.process()

        self.assertEqual([[extracted_heading[0], extracted_heading[1]]
                         for extracted_heading in extracted_headings], headings)
        self.assertEqual(extracted_categories, categories)

    def test_heading_tree(self):
        with open(self.input_directory + "Algorithm.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        extracted_headings, extracted_categories = wtr.process()

        heading_tree = {"Algorithm": {'History': {},
                                      'Informal definition': {},
                                      'Formalization': {},
                                      'Expressing algorithms': {},
                                      'Design': {},
                                      'Computer algorithms': {},
                                      'Examples': {'Algorithm example': {},
                                                   "Euclid's algorithm": {"Computer language for Euclid's algorithm": {},
                                                                          "An inelegant program for Euclid's algorithm": {},
                                                                          "An elegant program for Euclid's algorithm": {}},
                                                   'Testing the Euclid algorithms': {},
                                                   'Measuring and improving the Euclid algorithms': {}},
                                      'Algorithmic analysis': {'Formal versus empirical': {},
                                                               'Execution efficiency': {}},
                                      'Classification': {'By implementation': {},
                                                         'By design paradigm': {},
                                                         'Optimization problems': {},
                                                         'By field of study': {},
                                                         'By complexity': {},
                                                         'Continuous algorithms': {}},
                                      'Legal issues': {},
                                      'History: Development of the notion of "algorithm"': {'Ancient Near East': {},
                                                                                            'Discrete and distinguishable symbols': {},
                                                                                            'Manipulation of symbols as "place holders" for numbers: algebra': {},
                                                                                            'Cryptographic algorithms': {},
                                                                                            'Mechanical contrivances with discrete states': {},
                                                                                            'Mathematics during the 19th century up to the mid-20th century': {},
                                                                                            'Emil Post (1936) and Alan Turing (1936–37, 1939)': {},
                                                                                            'J.B. Rosser (1939) and S.C. Kleene (1943)': {},
                                                                                            'History after 1950': {}},
                                      'See also': {},
                                      'Notes': {},
                                      'Bibliography': {},
                                      'Further reading': {},
                                      'External links': {}}}

        extracted_heading_tree = wtr.heading_tree(extracted_headings)

        self.assertEqual(extracted_heading_tree, heading_tree)

    def test_section_tree_raw(self):
        with open(self.input_directory + "Dummy.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        extracted_headings, extracted_categories = wtr.process()

        section_tree = wtr.section_tree(extracted_headings, False)

        extracted_subsection_1 = section_tree["subsections"][0]

        self.assertEqual(extracted_subsection_1["name"], "Section 1")
        self.assertEqual(extracted_subsection_1["level"], 2)
        self.assertEqual(extracted_subsection_1["parent"], "Dummy")
        self.assertEqual(extracted_subsection_1["path"], "Dummy|Section 1")
        self.assertEqual(
            extracted_subsection_1["text"], "This is the section 1 text with some markup &lt;ref&gt; and a ref {{cite ref2}}.\n\n")

    def test_section_tree_clean(self):
        with open(self.input_directory + "Dummy.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        extracted_headings, extracted_categories = wtr.process()

        section_tree = wtr.section_tree(extracted_headings, True)

        self.assertEqual(section_tree["name"], "Dummy")
        self.assertEqual(section_tree["level"], 1)
        self.assertEqual(section_tree["parent"], None)
        self.assertEqual(section_tree["path"], "Dummy")
        self.assertEqual(section_tree["text"],
                         "'''Dummy''' is just a dummy article.")

        extracted_subsection_1 = section_tree["subsections"][0]

        self.assertEqual(extracted_subsection_1["name"], "Section 1")
        self.assertEqual(extracted_subsection_1["level"], 2)
        self.assertEqual(extracted_subsection_1["parent"], "Dummy")
        self.assertEqual(extracted_subsection_1["path"], "Dummy|Section 1")
        self.assertEqual(
            extracted_subsection_1["text"], "This is the section 1 text with some markup and a ref .")

        extracted_subsection_1_1 = extracted_subsection_1["subsections"][0]

        self.assertEqual(extracted_subsection_1_1["name"], "Section 1.1")
        self.assertEqual(extracted_subsection_1_1["level"], 3)
        self.assertEqual(extracted_subsection_1_1["parent"], "Section 1")
        self.assertEqual(
            extracted_subsection_1_1["path"], "Dummy|Section 1|Section 1.1")
        self.assertEqual(
            extracted_subsection_1_1["text"], "This is a subsection.")

        extracted_subsection_1_1_1 = extracted_subsection_1_1["subsections"][0]

        self.assertEqual(extracted_subsection_1_1_1["name"], "Section 1.1.1")
        self.assertEqual(extracted_subsection_1_1_1["level"], 4)
        self.assertEqual(extracted_subsection_1_1_1["parent"], "Section 1.1")
        self.assertEqual(
            extracted_subsection_1_1_1["path"], "Dummy|Section 1|Section 1.1|Section 1.1.1")
        self.assertEqual(
            extracted_subsection_1_1_1["text"], "This is a subsubsection.")

        extracted_subsection_2 = section_tree["subsections"][1]

        self.assertEqual(extracted_subsection_2["name"], "Section 2")
        self.assertEqual(extracted_subsection_2["level"], 2)
        self.assertEqual(extracted_subsection_2["parent"], "Dummy")
        self.assertEqual(extracted_subsection_2["path"], "Dummy|Section 2")
        self.assertEqual(
            extracted_subsection_2["text"], "Here's the rest of the text.")

    def test_find_heading(self):

        # Algorithm has a top-level history section without subsections AND a top-level section with 'history' as a substring

        with open(self.input_directory + "Algorithm.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        history_results = wtr.find_heading(
            "history", wtr.heading_tree(wtr.process()[0]))

        self.assertEqual(history_results[0], ["Algorithm", "History"])
        self.assertEqual(history_results[1], [
                         "Algorithm", 'History: Development of the notion of "algorithm"'])
        self.assertEqual(history_results[2], [
                         'Algorithm', 'History: Development of the notion of "algorithm"', 'History after 1950'])

        # Aluminium has a top-level history section without subsections

        with open(self.input_directory + "Aluminium.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        history_results = wtr.find_heading(
            "history", wtr.heading_tree(wtr.process()[0]))

        self.assertEqual(history_results[0], ["Aluminium", "History"])

        # Animation has a top-level history section with subsections

        with open(self.input_directory + "Animation.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        history_results = wtr.find_heading(
            "history", wtr.heading_tree(wtr.process()[0]))

        self.assertEqual(history_results[0], ["Animation", "History"])

        # Astronomer does not have a history section

        with open(self.input_directory + "Astronomer.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        history_results = wtr.find_heading(
            "history", wtr.heading_tree(wtr.process()[0]))

        self.assertEqual(history_results, [])

        # Axiom has a section with the substing 'historical'

        with open(self.input_directory + "Axiom.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        history_results = wtr.find_heading(
            "historical", wtr.heading_tree(wtr.process()[0]))

        self.assertEqual(history_results[0], [
                         "Axiom", "Historical development"])

        # Data compression has two history sections below a subsection

        with open(self.input_directory + "Data compression.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        history_results = wtr.find_heading(
            "history", wtr.heading_tree(wtr.process()[0]))

        self.assertEqual(history_results[0], [
                         "Data compression", "Uses", "Audio", "History"])
        self.assertEqual(history_results[1], [
                         "Data compression", "Uses", "Video", "History"])

    def test_find_section(self):
        with open(self.input_directory + "Dummy.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        extracted_headings, extracted_categories = wtr.process()

        section_tree = wtr.section_tree(extracted_headings, True)

        found_subsection_1 = wtr.find_section("Section 1", section_tree)

        self.assertEqual(found_subsection_1["name"], "Section 1")
        self.assertEqual(found_subsection_1["level"], 2)
        self.assertEqual(found_subsection_1["parent"], "Dummy")
        self.assertEqual(found_subsection_1["path"], "Dummy|Section 1")
        self.assertEqual(
            found_subsection_1["text"], "This is the section 1 text with some markup and a ref .")

        self.assertEqual(
            found_subsection_1["subsections"][0]["name"], "Section 1.1")
        self.assertEqual(found_subsection_1["subsections"][0]["level"], 3)
        self.assertEqual(
            found_subsection_1["subsections"][0]["parent"], "Section 1")
        self.assertEqual(
            found_subsection_1["subsections"][0]["path"], "Dummy|Section 1|Section 1.1")
        self.assertEqual(
            found_subsection_1["subsections"][0]["text"], "This is a subsection.")

        found_subsection_1_1 = wtr.find_section("Section 1.1", section_tree)

        self.assertEqual(found_subsection_1_1["name"], "Section 1.1")
        self.assertEqual(found_subsection_1_1["level"], 3)
        self.assertEqual(found_subsection_1_1["parent"], "Section 1")
        self.assertEqual(
            found_subsection_1_1["path"], "Dummy|Section 1|Section 1.1")
        self.assertEqual(found_subsection_1_1["text"], "This is a subsection.")

        self.assertEqual(
            found_subsection_1_1["subsections"][0]["name"], "Section 1.1.1")
        self.assertEqual(found_subsection_1_1["subsections"][0]["level"], 4)
        self.assertEqual(
            found_subsection_1_1["subsections"][0]["parent"], "Section 1.1")
        self.assertEqual(found_subsection_1_1["subsections"][0]
                         ["path"], "Dummy|Section 1|Section 1.1|Section 1.1.1")
        self.assertEqual(
            found_subsection_1_1["subsections"][0]["text"], "This is a subsubsection.")

        found_subsection_2 = wtr.find_section("Section 2", section_tree)

        self.assertEqual(found_subsection_2["name"], "Section 2")
        self.assertEqual(found_subsection_2["level"], 2)
        self.assertEqual(found_subsection_2["parent"], "Dummy")
        self.assertEqual(found_subsection_2["path"], "Dummy|Section 2")
        self.assertEqual(
            found_subsection_2["text"], "Here's the rest of the text.")

        self.assertEqual(found_subsection_2["subsections"], [])

    def test_get_text_of_section(self):
        with open(self.input_directory + "Dummy.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        extracted_headings, extracted_categories = wtr.process()

        section_tree = wtr.section_tree(extracted_headings, True)

        found_root_2 = wtr.find_section("Dummy", section_tree)

        self.assertEqual(wtr.get_text_of_section(found_root_2, 1).strip(),
                         "'''Dummy''' is just a dummy article.")
        self.assertEqual(wtr.get_text_of_section(found_root_2, 2).strip(),
                         ("'''Dummy''' is just a dummy article. This is the section 1 text with some markup and a ref . " +
                          "Here's the rest of the text."))
        self.assertEqual(wtr.get_text_of_section(found_root_2, 3).strip(),
                         ("'''Dummy''' is just a dummy article. This is the section 1 text with some markup and a ref . " +
                          "This is a subsection. Here's the rest of the text."))
        self.assertEqual(wtr.get_text_of_section(found_root_2, 4).strip(),
                         ("'''Dummy''' is just a dummy article. This is the section 1 text with some markup and a ref . " +
                          "This is a subsection. This is a subsubsection. Here's the rest of the text."))

        found_subsection_1 = wtr.find_section("Section 1", section_tree)

        self.assertEqual(wtr.get_text_of_section(found_subsection_1, 2).strip(),
                         "This is the section 1 text with some markup and a ref .")
        self.assertEqual(wtr.get_text_of_section(found_subsection_1, 3).strip(),
                         "This is the section 1 text with some markup and a ref . This is a subsection.")
        self.assertEqual(wtr.get_text_of_section(found_subsection_1, 4).strip(),
                         "This is the section 1 text with some markup and a ref . This is a subsection. This is a subsubsection.")

        found_subsection_2 = wtr.find_section("Section 2", section_tree)

        self.assertEqual(wtr.get_text_of_section(found_subsection_2, 2).strip(),
                         "Here's the rest of the text.")

    def test_has_category(self):
        with open(self.input_directory + "Axiom.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())

        extracted_headings, extracted_categories = wtr.process()

        self.assertEqual(wtr.has_category(
            "Mathematical axioms", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Ancient Greek philosophy", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Concepts in ancient Greek metaphysics", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Concepts in epistemology", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Concepts in ethics", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Concepts in logic", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Concepts in metaphysics", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Concepts in the philosophy of science", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Deductive reasoning", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Formal systems", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "History of logic", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "History of mathematics", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "History of philosophy", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "History of science", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Intellectual history", extracted_categories), True)
        self.assertEqual(wtr.has_category("Logic", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Mathematical logic", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Mathematical terminology", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Philosophical terminology", extracted_categories), True)
        self.assertEqual(wtr.has_category(
            "Reasoning", extracted_categories), True)

    def test_get_references(self):
        with open(self.input_directory + "Axiom.json") as file:
            data = load(file)

        wtr = WikitextReader(*data.values())
        references = wtr.get_references()
        self.assertEqual(len(references), 3)
        self.assertEqual(references[0],
                         {"cite":"journal",
                          "first":"Penelope",
                          "last":"Maddy",
                          "journal":"Journal of Symbolic Logic",
                          "title":"Believing the Axioms, I",
                          "volume":"53",
                          "issue":"2",
                          "date":"Jun 1988",
                          "pages":"481\u2013511",
                          "doi":"10.2307/2274520",
                          "jstor":"2274520"})
        self.assertEqual(references[1],
                         {"Cite":"web",
                          "url":"http://www.ptta.pl/pef/haslaen/a/axiom.pdf",
                          "title":"Axiom \u2014 Powszechna Encyklopedia Filozofii",
                          "website":"Polskie Towarzystwo Tomasza z Akwinu"})
        self.assertEqual(references[2],
                         {"cite":"Q",
                          "Q26720682":""})

# def test_iterator(self):
##
##        titles = []
##        pageids = []
##        revids = []
##        texts = []
##
# with WikipediaDumpReader(self.input_filepath) as wdr:
# for title, pageid, revid, timestamp, text in wdr.line_iter():
# if title not in titles:
# titles.append(title)
# if pageid not in pageids:
# pageids.append(pageid)
# if revid not in revids:
# revids.append(revid)
# texts.append(text)
##
##        self.maxDiff = None
##        self.assertEqual(len(titles), 2)
##        self.assertEqual(titles[0], "1.6 Band")
##        self.assertEqual(titles[1], "Derek Panza")
##        self.assertEqual(len(pageids), 2)
##        self.assertEqual(pageids[0], "27121496")
##        self.assertEqual(pageids[1], "27121502")
##        self.assertEqual(len(revids), 193 - 11)
##        self.assertEqual(revids[0], "358506549")
##        self.assertEqual(revids[-1], "918238989")
##        self.assertEqual(len(texts), 193 - 11)
##
# with open("tests/data/first_text.txt") as file:
##            self.assertEqual(texts[0], "".join(file.readlines()))
# with open("tests/data/final_text.txt") as file:
##            self.assertEqual(texts[-1], "".join(file.readlines()))

if __name__ == "__main__":
    unittest.main()
