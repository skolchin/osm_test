from itertools import tee, islice, groupby
from collections import deque

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def consume(iterator, n=None):
    "Advance the iterator n-steps ahead. If n is None, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

def split_iterable(iterable, num_splits: int) -> list:
    """ Splits an iterable to given number of lists.

    :param iterable: iterable to split
    :type iterable: any

    :param num_splits: required number of splits
    :type num_splits: int

    :return list of lists

    Example:

        ..code-block:: python

        >> vec = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >> [x for x in split_iterable(vec, 3)]
        >> [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

    """
    if not num_splits:
        raise ValueError('num_splits must not be equal to zero')
    return list({k: [y[1] for y in g] for k, g in groupby(enumerate(iterable), lambda v: v[0] // num_splits)}.values())

vec = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

print([x for x in pairwise(vec)])
print([x for x in split_iterable(vec, 2)])
