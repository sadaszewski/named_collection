#
# Copyright (C) Stanislaw Adaszewski, 2019
# https://github.com/sadaszewski/named_collection
# https://algoholic.eu
# https://adared.ch
#
# License: BSD 2-clause "Simplified" License
#


from functools import reduce


def _either_positional_or_keyword_args(*args, **kwargs):
    if (len(args) > 0 and len(kwargs) > 0) or \
        (len(args) == 0 and len(kwargs) == 0):
        raise ValueError('Either positional or keyword arguments must be used')


class NamedCollection(object):
    @staticmethod
    def from_interleaved(*args):
        if len(args) % 2 != 0:
            raise ValueError('Even number of arguments is required')
        # args = list(args)
        args = [(args[i], args[i + 1]) \
            for i in range(0, len(args), 2)]
        return NamedCollection(*args)

    @staticmethod
    def from_dicts(*args):
        args = [ list(a.items()) \
            for a in args ]
        args = reduce(list.__add__, args)
        return NamedCollection(*args)

    def __init__(self, *args):
        d = self.__dict__
        item_keys = d['item-keys'] = []
        item_values = d['item-values'] = []
        item_dict = d['item-dict'] = {}

        for a in args:
            if isinstance(a, tuple):
                key, value = a
            else:
                key = None
                value = a

            if key is not None:
                key = str(key)

            item_keys.append(key)
            item_values.append(value)

            if key is None:
                continue

            if key in item_dict:
                raise ValueError('Duplicate keys not allowed')

            item_dict[key] = \
                len(item_keys) - 1

    def copy(self):
        d = self.__dict__
        item_keys = d['item-keys']
        item_values = d['item-values']

        item_values = [ val.copy() \
            if isinstance(val, NamedCollection) \
            else val \
            for val in item_values ]

        return NamedCollection(*zip(item_keys, item_values))

    def items(self):
        d = self.__dict__
        item_keys = d['item-keys']
        item_values = d['item-values']
        return ((k, item_values[i]) \
            for i, k in enumerate(item_keys))

    def _get_item_triples(self, index):
        d = self.__dict__
        item_keys = d['item-keys']
        item_values = d['item-values']
        item_dict = d['item-dict']

        if isinstance(index, list):
            res = []
            for idx in index:
                res += self._get_item_triples(idx)
            return res

        if isinstance(index, slice):
            keys = item_keys[index]
            values = item_values[index]
            indices = range(len(item_keys))
            indices = list(indices[index])
            print('keys:', keys, 'indices:', indices,
                'values:', values)
            res = list(zip(indices, keys, values))
            return res

        if isinstance(index, str):
            if index in item_dict:
                idx = item_dict[index]
                res = [(idx, item_keys[idx], item_values[idx])]
            else:
                res = []
            return res

        try:
            idx = int(index)
        except:
            raise ValueError(f'Unsupported index type: {index.__class__}')

        res = [(idx, item_keys[idx], item_values[idx])]
        return res

    def __getitem__(self, index):
        d = self.__dict__

        item_dict = d['item-dict']
        item_values = d['item-values']

        print(f'index: {index.__class__}')

        if isinstance(index, tuple):
            index, tail = index[0], index[1:]
            triples = self._get_item_triples(index)
            res = []
            for idx, k, v in triples:
                if len(tail) == 0:
                    res.append((k, v))
                else:
                    if isinstance(v, NamedCollection):
                        res.append((k, v[tail]))
                    else:
                        pass
            res = NamedCollection(*res)
            return res

        res = self._get_item_triples(index)
        if len(res) == 1:
            return res[0][2]
        else:
            res = list(map(lambda a: a[1:], res))
            res = NamedCollection(*res)
            return res

    def __getattr__(self, attr):
        res = self._get_item_triples(attr)
        if len(res) == 0:
            raise AttributeError
        if len(res) != 1:
            raise RuntimeError('Attribute returning multiple values should not happen')
        return res[0][2]

    def __setitem__(self, index, value):
        d = self.__dict__

        item_dict = d['item-dict']
        item_keys = d['item-keys']
        item_values = d['item-values']

        if isinstance(index, tuple):
            raise ValueError('Multi-indexing not supported for setting items')

        if isinstance(index, str):
            if index in item_dict:
                idx = item_dict[index]
                item_values[idx] = value
            else:
                item_keys.append(index)
                item_values.append(value)
                item_dict[index] = len(item_keys) - 1
            return

        try:
            idx = int(index)
        except:
            raise ValueError(f'Unsupported key for item setting: {index.__class__}')

        if idx < len(item_keys):
            item_values[idx] = value
        else:
            raise ValueError(f'Index out of bounds: {idx}')

    def __setattr__(self, attr, value):
        self[attr] = value

    def append(self, value):
        d = self.__dict__

        item_dict = d['item-dict']
        item_keys = d['item-keys']
        item_values = d['item-values']

        item_keys.append(None)
        item_values.append(value)

        item_dict[None] = len(item_keys) - 1

    def tolist(self):
        d = self.__dict__
        item_values = d['item-values']
        item_values = [ val.tolist() \
            if isinstance(val, NamedCollection) \
            else val \
            for val in item_values ]
        return item_values

    def todict(self):
        d = self.__dict__
        item_keys = d['item-keys']
        item_values = d['item-values']
        item_values = [ val.todict() \
            if isinstance(val, NamedCollection) \
            else val \
            for val in item_values ]
        res = {key: item_values[i] \
            for i, key in enumerate(item_keys) \
            if key is not None}
        return res

    def __repr__(self):
        d = self.__dict__
        item_keys = d['item-keys']
        item_values = d['item-values']
        res = '{' + ', '.join((f'{repr(k) + ": " if k is not None else ""}{repr(item_values[i])}' \
            for i, k in enumerate(item_keys))) + '}'
        return res

    def __len__(self):
        d = self.__dict__
        item_values = d['item-values']
        return len(item_values)

    def _update(self, other):
        if not isinstance(other, NamedCollection):
            raise ValueError('Update can be called only using another NamedCollection')

        d = self.__dict__
        item_values = d['item-values']
        item_dict = d['item-dict']

        other_d = other.__dict__
        other_keys = other_d['item-keys']
        other_values = other_d['item-values']

        for i, key in enumerate(other_keys):
            other_val = other_values[i]

            if key is None:
                if i >= len(self):
                    raise IndexError(f'Index out of bounds: {i}')

                val = self[i]

                if isinstance(val, NamedCollection) and \
                    isinstance(other_val, NamedCollection):
                    val._update(other_val)
                    continue

                self[i] = other_val
                continue

            if key not in item_dict:
                self[key] = other_val
                continue

            val = item_values[item_dict[key]]

            if isinstance(val, NamedCollection) and \
                isinstance(other_val, NamedCollection):
                val._update(other_val)
                continue

            self[key] = other_val

    def update(self, *args):
        res = self.copy()
        for a in args:
            res._update(a)
        return res

    def _apply_pipeline(self, *args, raw=False):
        d = self.__dict__
        item_values = d['item-values']
        item_keys = d['item-keys']
        res = []
        for i, val in enumerate(item_values):
            if not raw and isinstance(val, NamedCollection):
                val = val._apply_pipeline(*args)
            else:
                for fn in args:
                    val = fn(val)
            res.append((item_keys[i], val))
        res = NamedCollection(*res)
        return res

    def _apply_selective(self, *args, **kwargs):
        raw = args[0] \
            if len(args) > 0 \
            else False
        d = self.__dict__
        item_values = d['item-values']
        item_keys = d['item-keys']
        res = []
        for i, val in enumerate(item_values):
            key = item_keys[i]
            if not raw and isinstance(val, NamedCollection):
                val = val._apply_selective(**kwargs)
            else:
                if key in kwargs:
                    fn = kwargs[key]
                    val = fn(val)
            res.append((key, val))
        res = NamedCollection(*res)
        return res

    def apply(self, *args, **kwargs):
        _either_positional_or_keyword_args(*args, **kwargs)

        if len(args) > 0:
            return self._apply_pipeline(*args)
        else:
            return self._apply_selective(**kwargs)

    def raw_apply(self, *args, **kwargs):
        _either_positional_or_keyword_args(*args, **kwargs)

        return self._apply_pipeline(*args, raw=True) \
            if len(args) > 0 \
            else self._apply_selective(True, **kwargs)

    def __iter__(self):
        d = self.__dict__
        item_values = d['item-values']
        return iter(item_values)

nc = _nc = NamedCollection

#----------------------------------------------------------------

_nc.__doc__ = '''\
Combination of a list and a dictionary. NamedCollection provides
an easy way for dispatching shared logic.'''

_nc.__init__.__doc__ = '''\
Create a new instance using *args as the list of items. Items can
be values or (key, value) tuples. If no key is given the value
will be accessible only by index. '''

_nc.copy.__doc__ = '''\
Performs a partial deep-copy of this instance. Nested values of
type NamedCollection will be copied as well. Regular values will
be assigned by reference in the copies. '''

_nc.items.__doc__ = '''\
Returns a (key, value) iterator similarly to dict.items(). Note
that returned items with key equal to None are accessible only
by index. '''

_nc._get_item_triples.__doc__ = '''\
Returns (index, key, value) triples of items matching specified
indexing expression. list, slice, str and int index types are
supported. '''

_nc.__getitem__.__doc__ = '''\
Implements item retrieval using simple and multi-indexing.
Multi-indexing can be used to search in nested NamedCollection
values. '''

_nc.__getattr__.__doc__ = '''\
Implements item retrieval using attribute notation. Attribute-
based retrieval is a more limited form of index-based retrieval.
As attributes can only be of type str by definition, only a
single item with key equal to the specified attribute can be
retrieved. '''

_nc.__setitem__.__doc__ = '''\
Implements item setting using index notation. Multi-indexing
is currently not supported. '''

_nc.__setattr__.__doc__ = '''\
Implements item setting using attribute notation. '''

_nc.append.__doc__ = '''\
Append an item without a key. '''

_nc.tolist.__doc__ = '''\
Returns items as a list. '''

_nc.todict.__doc__ = '''\
Returns items as a dictionary. Items without a key are skipped. '''

_nc.__repr__.__doc__ = '''\
Returns a string representation of this NamedCollection. '''

_nc.__len__.__doc__ = '''\
Returns item count in this NamedCollection. '''

_nc._update.__doc__ = '''\
Performs in-place update of this NamedCollection with the
contents of another. '''

#----------------------------------------------------------------

_nc.update.__doc__ = '''\
Updates values using another NamedCollection. Values are NOT
updated in-place. A new copy is returned. '''

_nc._apply_pipeline.__doc__ = '''\
Apply a pipeline of functions to all items in this
NamedCollection. '''

_nc._apply_selective.__doc__ = '''\
Apply functions to values based on keys specified in **kwargs. '''

_nc.apply.__doc__ = '''\
Based on whether positional or keyword arguments are used, either
apply a pipeline of functions to all items in this
NamedCollection or apply functions to values based on keys
specified in **kwargs. Values are not modified in-place. A new
copy is returned. '''

_nc.raw_apply.__doc__ = '''\
Same as apply() but values of type NamedCollection are not
processed recursively.'''

_nc.__iter__.__doc__ = '''\
Returns an iterator over the values stored in this
NamedCollection. '''
