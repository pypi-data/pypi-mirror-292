
from typing import List, Callable, Any

from geogst.core.inspections.errors import *


def find_val(
        func: Callable[[List], Any],
        lst: List
) -> Any:
    """
    Applies a function to a list when not empty,
    otherwise return None.

    :param func: function to apply to the list.
    :type func: function.
    :param lst: list to be processed.
    :type lst: List. May be empty.
    :return: result of function application or None.
    :rtype: Any.
    """

    if lst:
        return func(lst)
    else:
        return None


def list2_to_list(list2):
    """
    input: a list of list
    output: a list
    """

    out_list = []
    for list1 in list2:
        for el in list1:
            out_list.append(el)

    return out_list


def list3_to_list(list3):
    """
    input: a list of list of list
    output: a list
    """

    out_list = []
    for list2 in list3:
        for list1 in list2:
            out_list += list1

    return out_list


def split_list(
    lst: List,
    splitter: Optional[Any] = None
) -> List[Optional[List[Any]]]:
    """
    Split list into list based on splitter.

    Examples:
    >>> lst = [1, 2, None, 3, 4]
    >>> split_list(lst)
    [[1, 2], [3, 4]]
    >>> lst = [1, 2, None, 3, 4, None]
    >>> split_list(lst)
    [[1, 2], [3, 4]]
    >>> lst = [None, None, 1, 2, None, None, 3, 4, None, None]
    >>> split_list(lst)
    [[1, 2], [3, 4]]
    >>> lst = [None, None, 1, 2, None, None, 3, 4, None, None, 5, 6, 7]
    >>> split_list(lst)
    [[1, 2], [3, 4], [5, 6, 7]]
    >>> lst = [1, 2]
    >>> split_list(lst)
    [[1, 2]]
    >>> lst = [None]
    >>> split_list(lst)
    []
    >>> lst = [None, 1]
    >>> split_list(lst)
    [[1]]
    """

    lst2 = []

    sblst = []

    for el in lst:

        is_splitter = False
        if splitter is None:
            if el is None:
                is_splitter = True
        else:
            if el == splitter:
                is_splitter = True

        if is_splitter:
            if sblst:
                lst2.append(sblst)
                sblst = []
        else:
            sblst.append(el)

    if sblst:
        lst2.append(sblst)

    return lst2


if __name__ == "__main__":

    import doctest
    doctest.testmod()


