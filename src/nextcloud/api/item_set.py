# -*- coding: utf-8 -*-
"""
Define collection of item.
"""


class ItemSet(list):
    """
    Item set is an iterable,
    but if only one item is present then values can be directly accessed.
    """

    def __init__(self, classobj, itemset):
        self._itemset = itemset
        self._class = classobj

    def __repr__(self):  # keep this to force loading _itemset as a list
        #pylint: disable=unnecessary-comprehension
        return repr([k for k in self._itemset])

    def __len__(self):
        return len(self._itemset)

    def __reversed__(self):
        for key in reversed(self._itemset):
            yield (key, self._mapping[key])

    def __getattribute__(self, name):
        if name not in ['_class', '_itemset']:
            if len(self._itemset) != 1:
                return None
            return object.__getattribute__(self._itemset[0], name)
        return object.__getattribute__(self, name)

    def __bool__(self):
        """ Test whether ``self`` is nonempty. """
        return bool(self._itemset)

    def __iter__(self):
        """ Return an iterator over ``self``. """
        for propset in self._itemset:
            yield propset

    def __getitem__(self, idx):
        return self._itemset[idx]

    def __setitem__(self, idx, value):
        self._itemset[idx] = value
