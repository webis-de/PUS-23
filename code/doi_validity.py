from bibliography.bibliography import Bibliography

if __name__ == "__main__":

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")

    with open("doi_validaity.txt", "w") as file:
        for bib in bibliography.bibentries.values():
            file.write(bib.bibkey + "\n")
            if not bib.doi_valid():
                file.write("\n" + str(bib.__dict__) + "\n\n")
    
