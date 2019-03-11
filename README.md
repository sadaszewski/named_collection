# named_collection
A flexible container mixing semantics of list, dictionary and NumPy array/Pandas dataframe in order to provide maximum flexibility for grouping and dispatching common work to selected subsets of variables.

Usage example:

```python
from named_collection import NamedCollection as nc

data = nc(*((release, DatasetsDownload(data_release=release)) \
  for release in ['train', 'test']))
data = data.apply(lambda a: \
  a.get_data('baseline', 'labs', 'vitals'))
data = data.apply(baseline=clean_baseline, labs=clean_labs,
  vitals=clean_vitals)
data = data.raw_apply(lambda a: \
  merge_data(a.baseline, a.labs, a.vitals))
train, test = train_test_split(data.train, test_size=.15)
data.train = nc( ('train', train), ('test', test) )
clf = make_clf(data.train.train)
pred = data.apply(test=lambda a: clf.pred(a))
print(pred.train.test)
print(pred.test)
```

Alternative construction:

```python
from named_collection import nc
nc = nc.from_interlaved
x=nc('a', 1, 'b', 2, 'c', nc('d', 3, 'e', 4, 'f', 5))
```
