from article.revision.revision import Revision
import unittest
from json import loads

class TestRevision(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Revision 51 (index 50) of CRISPR
        # https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=369962884
        with open("tests/revision1.json") as revision_file:
            cls.revision1_section_tree = Revision(**loads(revision_file.readline())).section_tree()
        # Revision 2092 (index 2091) of CRISPR
        # https://en.wikipedia.org/w/index.php?title=CRISPR&oldid=1009355338
        with open("tests/revision2.json") as revision_file:
            cls.revision2_section_tree = Revision(**loads(revision_file.readline())).section_tree()

    def test_section_tree_revision1(self):
        root_of_revision1 = self.revision1_section_tree
        self.assertEqual(["CRISPR Mechanism",
                          "CRISPR Spacers and Repeats",
                          "References",
                          "External links"],
                          [subsection.name for subsection in root_of_revision1.subsections])

    def test_section_tree_revision2(self):
        root_of_revision2 = self.revision2_section_tree
        self.assertEqual(["History",
                          "Locus structure",
                          "Mechanism",
                          "Evolution",
                          "Identification",
                          "Use by phages",
                          "Applications",
                          "See also",
                          "Notes",
                          "References",
                          "Further reading",
                          "External links"],
                          [subsection.name for subsection in root_of_revision2.subsections])
        root_History_of_revision2 = root_of_revision2.subsections[0]
        self.assertEqual(["Repeated sequences",
                          "CRISPR-associated systems",
                          "Cas9",
                          "Cas12a (formerly Cpf1)",
                          "Cas13 (formerly C2c2)"],
                         [subsection.name for subsection in root_History_of_revision2.subsections])
        root_Locus_structure_of_revision2 = root_of_revision2.subsections[1]
        self.assertEqual(["Repeats and spacers",
                          "CRISPR RNA structures",
                          "Cas genes and CRISPR subtypes"],
                         [subsection.name for subsection in root_Locus_structure_of_revision2.subsections])
        root_Mechanism_of_revision2 = root_of_revision2.subsections[2]
        self.assertEqual(["Spacer acquisition",
                          "Biogenesis",
                          "Interference"],
                         [subsection.name for subsection in root_Mechanism_of_revision2.subsections])
        root_Mechanism_Spacer_acquisition_of_revision2 = root_Mechanism_of_revision2.subsections[0]
        self.assertEqual(["Protospacer adjacent motifs",
                          "Insertion variants"],
                         [subsection.name for subsection in root_Mechanism_Spacer_acquisition_of_revision2.subsections])
        root_Evolution_of_revision2 = root_of_revision2.subsections[3]
        self.assertEqual(["Coevolution",
                          "Rates"],
                         [subsection.name for subsection in root_Evolution_of_revision2.subsections])
        root_Identification_of_revision2 = root_of_revision2.subsections[4]
        self.assertEqual([],
                         [subsection.name for subsection in root_Identification_of_revision2.subsections])
        root_Use_by_phages_of_revision2 = root_of_revision2.subsections[5]
        self.assertEqual([],
                         [subsection.name for subsection in root_Use_by_phages_of_revision2.subsections])
        root_Applications_of_revision2 = root_of_revision2.subsections[6]
        self.assertEqual(["CRISPR gene editing",
                          "CRISPR as diagnostic tool"],
                         [subsection.name for subsection in root_Applications_of_revision2.subsections])
        root_See_also_of_revision2 = root_of_revision2.subsections[7]
        self.assertEqual([],
                         [subsection.name for subsection in root_See_also_of_revision2.subsections])
        root_Notes_of_revision2 = root_of_revision2.subsections[8]
        self.assertEqual([],
                         [subsection.name for subsection in root_Notes_of_revision2.subsections])
        root_References_of_revision2 = root_of_revision2.subsections[9]
        self.assertEqual([],
                         [subsection.name for subsection in root_References_of_revision2.subsections])
        root_Further_reading_of_revision2 = root_of_revision2.subsections[10]
        self.assertEqual([],
                         [subsection.name for subsection in root_Further_reading_of_revision2.subsections])
        root_External_links_of_revision2 = root_of_revision2.subsections[11]
        self.assertEqual([],
                         [subsection.name for subsection in root_External_links_of_revision2.subsections])

    def test_find(self):
        self.assertEqual(["root", "CRISPR Mechanism", "CRISPR Spacers and Repeats", "References", "External links"],
                         [section.name for section in self.revision1_section_tree.find(strings=[""])])
        self.assertEqual(["CRISPR Mechanism", "CRISPR Spacers and Repeats", "References"],
                         [section.name for section in self.revision1_section_tree.find(strings=["Re", "CRISPR"])])

    def test_find_reference_section_revision1(self):
        reference_section_text_of_revision1 = \
          ('^ Sorek R, Kunin V, Hugenholtz P (2008). "CRISPR - a widespread system that provides acquired resistance against phages in bacteria and archaea". Nature Reviews '
          'Microbiology. 6: 181–6. doi:10.1038/nrmicro1793. Unknown parameter |month= ignored (help)CS1 maint: multiple names: authors list (link)\n'
          '\n'
          '^ Sorek R, Kunin V, Hugenholtz P (2008). "CRISPR - a widespread system that provides acquired resistance against phages in bacteria and archaea". Nature Reviews '
          'Microbiology. 6: 181–6. doi:10.1038/nrmicro1793.CS1 maint: multiple names: authors list (link)\n'
          '\n'
          '^ Pourcel C, Salvignol G, Vergnaud G (2005). "CRISPR elements in Yersinia pestis acquire new repeats by preferential uptake of bacteriophage DNA, and provide additional '
          'tools for evolutionary studies". Microbiology. 151: 653. doi:10.1099/mic.0.27437-0. PMID\xa015758212.CS1 maint: multiple names: authors list (link)\n'
          '\n'
          '^ Haft DH, Selengut J, Mongodin EF, Nelson KE (2005). "A guild of 45 CRISPR-associated (Cas) protein families and multiple CRISPR/Cas subtypes exist in prokaryotic '
          'genomes". PLoS Comput Biol. 1 (6): e60. doi:10.1371/journal.pcbi.0010060. PMID\xa016292354.CS1 maint: multiple names: authors list (link)\n'
          '\n'
          '^ Makarova KS, Grishin NV, Shabalina SA, Wolf YI, Koonin EV (2006). "A putative RNA-interference-based immune system in prokaryotes: computational analysis of the '
          'predicted enzymatic machinery, functional analogies with eukaryotic RNAi, and hypothetical mechanisms of action". Biol Direct. 1: 7. doi:10.1186/1745-6150-1-7. PMID\xa0'
          '16545108.CS1 maint: multiple names: authors list (link)\n'
          '\n'
          '^ Barrangou R, Fremaux C, Deveau H, Richards M, Boyaval P, Moineau S, Romero DA, Horvath P. (2007). "CRISPR provides acquired resistance against viruses in prokaryotes". '
          'Science. 315 (5819): 1709. doi:10.1126/science.1138140. PMID\xa017379808.CS1 maint: multiple names: authors list (link)\n'
          '\n'
          '^ Andersson AF, Banfield JF (2008). "Virus population dynamics and acquired virus resistance in natural microbial communities". Science. 320: 1047. '
          'doi:10.1126/science.1157358. PMID\xa018497291.\n'
          '\n'
          '^ Brouns SJJ, Jore MM, Lundgren M, Westra ER, Slijkhuis RJH, Snijders APL, Dickman MJ, Makarova KS, Koonin EV, Van der Oost J (2008). "Small CRISPR RNAs Guide Antiviral '
          'Defense in Prokaryotes". Science. 321: 960. doi:10.1126/science.1159689. PMID\xa018703739.CS1 maint: multiple names: authors list (link)')
        reference_section_of_revision1 = self.revision1_section_tree.find(strings=["references"], lower=True)[0]
        self.assertEqual(reference_section_text_of_revision1, reference_section_of_revision1.get_text())

if __name__ == "__main__":
    unittest.main()



