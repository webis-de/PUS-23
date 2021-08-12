from os.path import sep

def stopwords(stopwords_filepath):
    """
    Reads a list of stopwords from a file.
    IMPORTANT: No tokenisation - only one word per line!

    Args:
        stopwords_filepath: The path to the stopwords file.

    Returns:
        A list of stopword strings. If the file cannot be found,
        a message is printed and an empty list is returned.
    """
    stopwords = set()
    if stopwords_filepath == "":
        return stopwords
    try:
        with open (stopwords_filepath) as file:
            for line in file:
                line = line.strip()
                stopwords.add(line)
                stopwords.add(line[0].upper() + line[1:])
    except FileNotFoundError:
        print("Stopword file (" + stopwords_filepath +") not found.")
    return stopwords

def abbreviations(abbreviations_filepath):
    """
    Reads a list of abbreviations from a file.
    IMPORTANT: No tokenisation - only one word per line!

    Args:
        abbreviations_filepath: The path to the abbreviations file.

    Returns:
        A list of abbreviation strings. If the file cannot be found,
        a message is printed and an empty list is returned.
    """
    abbreviations = set()
    if abbreviations_filepath == "":
        return abbreviations
    try:
        with open (abbreviations_filepath) as file:
            for line in file:
                line = line.strip()
                abbreviations.add(line)
                abbreviations.add(line.lower())
    except FileNotFoundError:
        print("Abbreviations file (" + abbreviations_filepath +") not found.")
    return abbreviations

def contractions(contractions_filepath):
    """
    Reads a list of stopwords from a file.
    IMPORTANT: No tokenisation - only one word per line!

    Args:
        contractions_filepath: The path to the contractions file.

    Returns:
        A list of contraction strings. If the file cannot be found,
        a message is printed and an empty list is returned.
    """
    contractions = set()
    if contractions_filepath == "":
        return contractions
    try:
        with open (contractions_filepath) as file:
            for line in file:
                line = line.strip()
                contractions.add(tuple(line.strip().split("-")))
                contractions.add(tuple([word[0].upper() + word[1:] for word in line.strip().split("-")]))
    except FileNotFoundError:
        print("Contractions file (" + contractions_filepath +") not found.")
    return contractions
