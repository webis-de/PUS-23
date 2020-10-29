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

def powerset(items, result = [], subset = [], min_len_sub = 1):
    """
    Calculate the powerset of subsets of given list.

    Args:
        items: The list for which the powerset should be calculated.
        result: The resulting powerset.
        min_len_sub: The minimum length of subsets to return.        
    """
    if len(items) + len(subset) < min_len_sub:
        return
    elif not items:
        result.append(set(subset))
    else:
        powerset(items[1:], result, subset + [items[0]], min_len_sub)
        powerset(items[1:], result, subset, min_len_sub)
    return sorted(result, key = lambda x: len(x))

if __name__ == "__main__":

    print(flatten_list_of_lists([[1,2,3],["a","b","c","d","e"]]))

    items = list(["a","b","c","d","e"])

    print(powerset(items, min_len_sub = 2))
