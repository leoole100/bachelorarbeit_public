"""
Utility functions not specific to any one module.
"""
def nm_to_ev(nm):
    return 1239.84193/nm
def ev_to_nm(ev):
    return 1239.84193/ev

import typing
from itertools import groupby

def groupby_list(x: typing.Iterable, key: typing.Callable) -> typing.Set[typing.Tuple]:
	"""
	groupby like SQL groupby
	Note: Has to sort the entire list
	"""
	d = {}
	for k, v in groupby(sorted(x, key=key), key=key):
		d[k] = list(v)

	return d