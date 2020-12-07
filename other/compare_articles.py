from os import popen
from glob import glob
from json import loads
from os.path import basename, sep

def check1(directory1, directory2):

    directory1 = {basename(path):path for path in glob(directory1 + sep + "*") if ".txt" not in path}
    directory2 = {basename(path):path for path in glob(directory2 + sep + "*") if ".txt" not in path}

    for file in directory1:
        
        if file in directory2:
            
            checksum1 = popen("sha256sum " + directory1[file]).read().strip()
            checksum2 = popen("sha256sum " + directory2[file]).read().strip()
            print(checksum1)
            print(checksum2)
            if checksum1.split(" ")[0] != checksum2.split(" ")[0]:
                print("MISSMATCH")
            print()

def check2(file1, file2):
    print("Comparing ", file1, " and ", file2, "\n")
    with open(file1) as f1:
        lines1 = f1.readlines()
    with open(file2) as f2:
        lines2 = f2.readlines()

    print("Number of lines in file one:",len(lines1))
    print("Number of lines in file two:",len(lines2))

    print("Lines differing:")
    diffs = []
    for i in range(len(lines1)):
        if lines1[i] != lines2[i]:
            diffs.append(i)
    print(diffs)
    print()
    LINE = 128
    print("Comparing line", LINE)
    print("Matching?", lines1[LINE] == lines2[LINE])
    l1 = loads(lines1[LINE])
    print("revid file one:",l1["revid"])
    print("timestamp file one:",l1["timestamp"])
    with open("file_1.html", "w") as html_file_1:
        html_file_1.write(l1["html"])
    l2 = loads(lines2[LINE])
    print("revid file two:",l1["revid"])
    print("timestamp file two:",l1["timestamp"])
    with open("file_2.html", "w") as html_file_2:
        html_file_2.write(l2["html"])

    for key in l1:
        print(key, l1[key] == l2[key])
    print()


check2("articles/CRISPR_interference_en","articles_old_updated/CRISPR_interference_en")

