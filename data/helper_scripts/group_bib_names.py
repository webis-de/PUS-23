def braces(name):
    if " " in name:
        return "{" + name + "}"
    else:
        return name

with open("tracing-innovations-lit_new.bib", "w") as new_file:
    with open("tracing-innovations-lit.bib") as old_file:
        for line in old_file:
            if line.startswith("  Author"):
                new_file.write(line[:25])
                
                authors = [[name.strip() for name in author.split(",")] for author in line[25:-3].split(" and ")]
                
                new_file.write(" and ".join([braces(name[1]) + " " + braces(name[0]) for name in authors]))

                new_file.write(line[-3:])
            else:
                new_file.write(line)


