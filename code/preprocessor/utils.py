from os.path import sep

def stopwords(stopwords_filepath):
    """
    Reads a list of stopwords from a file.
    IMPORTANT: No tokenisation - only one word per line!

    Args:
        stopwords_filepath: The path to the stopwords file.

    Returns:
        A list of stopword strings. If the file cannot be found, a message is printed
        and an empty list is returned.
    """
    stopwords = set()
    if stopwords_filepath == "":
        return stopwords
    try:
        with open (stopwords_filepath) as file:
            for word in file:
                word = word.strip()
                stopwords.add(word)
                stopwords.add(word[0].upper() + word[1:])
    except FileNotFoundError:
        try:
            with open ("code" + sep + stopwords_filepath) as file:
                for word in file:
                    word = word.strip()
                    stopwords.add(word)
                    stopwords.add(word[0].upper() + word[1:])
        except FileNotFoundError:
            print("Stopword file (" + stopwords_filepath +") not found.")
    return stopwords

def abbreviations(abbreviations_filepath):
    """
    Reads a list of stopwords from a file.
    IMPORTANT: No tokenisation - only one word per line!

    Args:
        abbreviations_filepath: The path to the abbreviations file.

    Returns:
        A list of abbreviation strings. If the file cannot be found, a message is printed
        and an empty list is returned.
    """
    abbreviations = set()
    if abbreviations_filepath == "":
        return abbreviations
    try:
        with open (abbreviations_filepath) as file:
            for word in file:
                word = word.strip()
                abbreviations.add(word)
                abbreviations.add(word.lower())
    except FileNotFoundError:
        try:
            with open ("code" + sep + abbreviations_filepath) as file:
                for word in file:
                    word = word.strip()
                    abbreviations.add(word)
                    abbreviations.add(word.lower())
        except FileNotFoundError:
            print("Abbreviations file (" + abbreviations_filepath +") not found.")
    return abbreviations
