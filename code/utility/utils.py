from itertools import combinations

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

def calc_powerset(items, result = [], subset = [], min_len_sub = 1):
    """
    Calculate the powerset of subsets of given list.

    Args:
        items: The list for which the powerset should be calculated.
        result: The resulting powerset.
        subset: Holds subset during recursion.
        min_len_sub: The minimum length of subsets to return.
    Returns:
        The powerset.
    """
    if len(items) + len(subset) < min_len_sub:
        return ()
    elif not items:
        result.append(tuple(subset))
    else:
        calc_powerset(items[1:], result, subset + [items[0]], min_len_sub)
        calc_powerset(items[1:], result, subset, min_len_sub)
    return result

def powerset1(items, min_len_sub):
    """
    Calculate the powerset of given list.

    Args:
        items: The list for which the powerset should be calculated.
        min_len_sub: The minimum length of subsets to return.
    Returns:
        The powerset.
    """
    return calc_powerset(items, [], [], min_len_sub)

def powerset2(items, min_len):
    """
    Calculate the powerset of given list.

    Args:
        items: The list for which the powerset should be calculated.
    Returns:
        The powerset.
    """
    return [x for length in range(len(items)+1, min_len-1, -1) for x in combinations(items, length)]

def powerset3(items, min_len):
    """
    Calculate the powerset of given list.

    Args:
        items: The list for which the powerset should be calculated.
    Returns:
        The powerset.
    """
    return [x for length in range(len(items)+1, min_len-1, -1) for x in my_combinations(items, length, [], [])]

def my_combinations(items, r, result, subset):
    if r > len(items):
        result.append(subset)
    else:
        for i in range(r):
            my_combinations(items[i+1:], r-i, result, subset + [items[i]])
    return result

if __name__ == "__main__":

    from datetime import datetime

    #print(comb([1,2,3,4,5],[],[],4))

    print(flatten_list_of_lists([[1,2,3],["a","b","c","d","e"]]))
    
    items = list([1,2,3,4,5,6,7,8,9,10,11,12,13])

    start = datetime.now()
    ps1 = powerset1(items, min_len_sub = 0)
    print(ps1)
    print(datetime.now() - start)

    start = datetime.now()
    ps2 = powerset2(items, min_len = 0)
    print(ps2)
    print(datetime.now() - start)

    start = datetime.now()
    ps3 = powerset3(items, min_len = 0)
    print(ps3)
    print(datetime.now() - start)
