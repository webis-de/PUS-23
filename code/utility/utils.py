from itertools import combinations
from Levenshtein import distance

def flatten_list_of_lists(list_of_lists):
    """
    Flattens list of lists to one list, i.e.
    [[e1,e2,e3],[e4,e5,e6],...] => [e1,e2,e3,e4,e5,e6,...]

    Args:
        list_of_lists: A list of lists.

    Returns:
        A flattened list of elements of each list in the list of lists.
    """
    return [item for sublist in list_of_lists for item in sublist]

def powerset(items, min_len):
    """
    Calculate the powerset of given list.

    Args:
        items: The list for which the powerset should be calculated.
    Returns:
        The powerset.
    """
    return [x for length in range(len(items)+1, min_len-1, -1) for x in combinations(items, length)]

def levenshtein_custom(word1, word2, verbose = False):
    """
    Calculate the edit distance between two words.

    Args:
        word1: The first string.
        word2: The second string.
    Returns:
        The edit distance between the two strings.
    """
    k = len(word1) + 1
    l = len(word2) + 1
    matrix = [[0 for x in range(0, l)] for y in range(0, k)]

    for i in range(0, k):
        matrix[i][0] = i

    for j in range(0, l):
        matrix[0][j] = j
    
    for i in range(0, k-1):
        for j in range(0, l-1):
            matrix[i+1][j+1] = min([matrix[i][j+1] + 1, matrix[i+1][j] + 1, matrix[i][j] + int(word1[i] != word2[j])])
    if verbose:
        print("    " + " ".join((x for x in word2)))
        for i in range(0, len(matrix)):
            print((" " + word1)[i] + " " + " ".join(str(x) for x in matrix[i]))
        print("\n" + "EDIT DISTANCE = " + str(matrix[len(word1)][len(word2)]) + "\n")
    return matrix[-1][-1]

def levenshtein(word1, word2, verbose = False):
    """
    Calculate the edit distance between two words.

    Args:
        word1: The first string.
        word2: The second string.
    Returns:
        The edit distance between the two strings.
    """
    edit_distance = distance(word1, word2)
    if verbose:
        print("\n" + "EDIT DISTANCE = " + str(edit_distance) + "\n")
    return edit_distance

if __name__ == "__main__":

    from datetime import datetime

    word1 = "Clustered Regularly Interspaced Short Palindrome Repeats (CRISPRs) Have Spacers of Extrachromosomal Origin"
    word2 = "Clustered Regularly-Interspaced Short Palindrome Repeats CRISPRs Have Spacers of Extrachromosomal Origin"

    start = datetime.now()
    print(levenshtein(word1,word2))
    print(datetime.now() - start)

    start = datetime.now()
    print(levenshtein_custom(word1,word2))
    print(datetime.now() - start)
