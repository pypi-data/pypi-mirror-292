"""Functions for, instead of values and key functions, key-value pairs.

    A key function or collation function is a callable that returns a
    value used for sorting or ordering. For example, locale.strxfrm() is
    used to produce a sort key that is aware of locale specific sort
    conventions.

    A number of tools in Python accept key functions to control how
    elements are ordered or grouped. They include min(), max(),
    sorted(), list.sort(), heapq.merge(), heapq.nsmallest(),
    heapq.nlargest(), and itertools.groupby().

    -- https://docs.python.org/3/glossary.html#term-key-function

Instead of a key function and an iterable of values, an iterable of
key-value pairs each function of this module takes.

To import it run

>>> import keysvalues

Functions
---------
minimum
    Like min, find the value with the least key.
maximum
    Like max, find the value with the greatest key.
sort
    Like sorted, sort values by keys.
group
    Like itertools.groupby, group values by keys.
gather_in
    Return a function that gathers values by keys.
list_gather
    Gather values in lists by keys.
set_gather
    Gather values in sets by keys.
dict_gather
    Gather values in dicts by keys.
counter_gather
    Gather values in Counters by keys.
"""

import collections
import functools
import itertools
import operator


def minimum(items):
    """Like min, find the value with the least key.

    items ought to be a non-empty iterable each member whereof is an
    iterable of a key and a value.

    >>> keysvalues.minimum([(1, 8), (0, 9), (0, 8)])
    9
    """
    iterators = map(iter, items)
    iterator_min = min(iterators, key=next)
    return next(iterator_min)


def maximum(items):
    """Like max, find the value with the greatest key.

    items ought to be a non-empty iterable each member whereof is an
    iterable of a key and a value.

    >>> keysvalues.maximum([(0, 9), (1, 8), (1, 9)])
    8
    """
    iterators = map(iter, items)
    iterator_max = max(iterators, key=next)
    return next(iterator_max)


def sort(items, *, reverse=False):
    """Like sorted, sort values by keys.

    items ought to be an iterable each member whereof is an iterable of
    a key and a value.

    >>> keysvalues.sort([(2, 7), (1, 9), (0, 8), (1, 8)])
    [8, 9, 8, 7]
    >>> keysvalues.sort([(2, 7), (1, 9), (0, 8), (1, 8)], reverse=True)
    [7, 9, 8, 8]
    >>> keysvalues.sort([])
    []
    """
    iterators = map(iter, items)
    iterators_sorted = sorted(iterators, key=next, reverse=reverse)
    return [next(iterator) for iterator in iterators_sorted]


def group(items):
    """Like itertools.groupby, group values by keys.

    items ought to be an iterable each member whereof is an iterable of
    a key and a value.

    >>> groups = keysvalues.group([(1, 8), (1, 9), (0, 7), (0, 7), (1, 7)])
    >>> [(key, list(group)) for key, group in groups]
    [(1, [8, 9]), (0, [7, 7]), (1, [7])]
    >>> list(keysvalues.group([]))
    []
    """
    iterators = map(iter, items)
    groups = itertools.groupby(iterators, next)
    return ((key, map(next, group_)) for key, group_ in groups)


def gather_in(make, grow):
    """Return a function that gathers values by keys.

    The result's parameter list is (items, depth=1). items ought to be
    an iterable and depth a number such that each member of items is an
    iterable of depth keys and a value.

    The result returns a defaultdict of defaultdicts of defaultdicts of
    ... defaultdicts of gatherings made by make and grown by grow where
    the number of levels of defaultdicts is depth.
    """

    def make_gatherings(depth=1):
        if depth:
            return collections.defaultdict(lambda: make_gatherings(depth - 1))
        return make()

    def gather(items, depth=1):
        gatherings = make_gatherings(depth)
        for *keys, value in items:
            gathering = functools.reduce(operator.getitem, keys, gatherings)
            grow(gathering, value)
        return gatherings

    return gather


list_gather = gather_in(list, list.append)
list_gather.__doc__ = """Gather values in lists by keys.

    To make reading easier, defaultdicts are written as dicts.

    >>> keysvalues.list_gather([(2, 0), (3, 1), (2, 1), (2, 0)])
    {2: [0, 1, 0], 3: [1]}
    >>> keysvalues.list_gather([(5, 2, 0), (5, 3, 1), (4, 2, 1), (5, 2, 0)], depth=2)
    {5: {2: [0, 0], 3: [1]}, 4: {2: [1]}}
    >>> keysvalues.list_gather([(0,), (1,), (1,), (0,)], depth=0)
    [0, 1, 1, 0]
    >>> keysvalues.list_gather([])
    {}
    >>> keysvalues.list_gather([], depth=0)
    []
    """

set_gather = gather_in(set, set.add)
set_gather.__doc__ = """Gather values in sets by keys.

    To make reading easier, defaultdicts are written as dicts.

    >>> keysvalues.set_gather([(2, 0), (3, 1), (2, 1), (2, 0)])
    {2: {0, 1}, 3: {1}}
    >>> keysvalues.set_gather([(5, 2, 0), (5, 3, 1), (4, 2, 1), (5, 2, 0)], depth=2)
    {5: {2: {0}, 3: {1}}, 4: {2: {1}}}
    >>> keysvalues.set_gather([(0,), (1,), (1,), (0,)], depth=0)
    {0, 1}
    >>> keysvalues.set_gather([])
    {}
    >>> keysvalues.set_gather([], depth=0)
    set()
    """


def update(gathering, item):
    """Update gathering with item."""
    return gathering.update([item])


dict_gather = gather_in(dict, update)
dict_gather.__doc__ = """Gather values in dicts by keys.

    To make reading easier, defaultdicts are written as dicts.

    >>> keysvalues.dict_gather([(5, (2, 0)), (5, (3, 1)), (4, (2, 1)), (5, (2, 0))])
    {5: {2: 0, 3: 1}, 4: {2: 1}}
    >>> keysvalues.dict_gather(
    ...     [(7, 5, (2, 0)), (8, 5, (3, 1)), (6, 4, (2, 1)), (8, 5, (2, 0))],
    ...     depth=2,
    ... )
    {7: {5: {2: 0}}, 8: {5: {3: 1, 2: 0}}, 6: {4: {2: 1}}}
    >>> keysvalues.dict_gather([((2, 0),), ((3, 1),), ((2, 1),), ((2, 0),)], depth=0)
    {2: 0, 3: 1}
    >>> keysvalues.dict_gather([])
    {}
    >>> keysvalues.dict_gather([], depth=0)
    {}
    """

counter_gather = gather_in(collections.Counter, update)
counter_gather.__doc__ = """Gather values in Counters by keys.

    To make reading easier, defaultdicts are written as dicts.

    >>> keysvalues.counter_gather([(2, 0), (3, 1), (2, 1), (2, 0)])
    {2: Counter({0: 2, 1: 1}), 3: Counter({1: 1})}
    >>> keysvalues.counter_gather([(5, 2, 0), (5, 3, 1), (4, 2, 1), (5, 2, 0)], depth=2)
    {5: {2: Counter({0: 2}), 3: Counter({1: 1})}, 4: {2: Counter({1: 1})}}
    >>> keysvalues.counter_gather([(0,), (1,), (1,), (0,)], depth=0)
    Counter({0: 2, 1: 2})
    >>> keysvalues.counter_gather([])
    {}
    >>> keysvalues.counter_gather([], depth=0)
    Counter()
    """
