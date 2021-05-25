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

    def __lt__(self, other): return self._itemset <  self.__cast(other)
    def __le__(self, other): return self._itemset <= self.__cast(other)
    def __eq__(self, other): return self._itemset == self.__cast(other)
    def __gt__(self, other): return self._itemset >  self.__cast(other)
    def __ge__(self, other): return self._itemset >= self.__cast(other)
    def __cast(self, other):
        return other._itemset if isinstance(other, ItemSet) else other
    def __contains__(self, item): return item in self._itemset
    def __len__(self): return len(self._itemset)
    def __getitem__(self, idx): return self._itemset[idx]
    def __setitem__(self, idx, value): self._itemset[idx] = value
    def __delitem__(self, i): del self._itemset[i]
    def __getslice__(self, *args): return self._itemset.__getslice__(*args)
    def __setslice__(self, *args): self._itemset.__setslice__(*args)
    def __add__(self, other):
        if isinstance(other, ItemSet):
            return self.__class__(self._itemset + other._itemset)
        elif isinstance(other, type(self._itemset)):
            return self.__class__(self._itemset + other)
        return self.__class__(self._itemset + list(other))
    def __radd__(self, other):
        if isinstance(other, ItemSet):
            return self.__class__(other._itemset + self._itemset)
        elif isinstance(other, type(self._itemset)):
            return self.__class__(other + self._itemset)
        return self.__class__(list(other) + self._itemset)
    def __iadd__(self, other):
        if isinstance(other, ItemSet):
            self._itemset += other._itemset
        elif isinstance(other, type(self._itemset)):
            self._itemset += other
        else:
            self._itemset += list(other)
        return self
    def __mul__(self, n):
        return self.__class__(self._itemset*n)
    __rmul__ = __mul__
    def __imul__(self, n):
        self._itemset *= n
        return self
    def append(self, item): self._itemset.append(item)
    def clear(self): self._itemset.clear()
    def copy(self): return self.__class__(self)
    def count(self, item): return self._itemset.count(item)
    def extend(self, other):
        if isinstance(other, ItemSet):
            self._itemset.extend(other._itemset)
        else:
            self._itemset.extend(other)
    def index(self, item, *args): return self._itemset.index(item, *args)
    def insert(self, i, item): self._itemset.insert(i, item)
    def pop(self, i=-1): return self._itemset.pop(i)
    def remove(self, item): self._itemset.remove(item)
    def reverse(self): self._itemset.reverse()
    def sort(self, *args, **kwds): self._itemset.sort(*args, **kwds)
