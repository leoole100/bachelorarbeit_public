"""
This is a script to plot the look at the recorded photoluminescence spectra
"""
# %%

import warnings
from lib.preamble import *

# %%

from lib.preamble import *

paths = glob("../data/2023-10-*/d*.asc")
paths += glob("../data/2023-11-*/d*.asc")

def load_file(p):
	data = np.loadtxt(p)
	wavelength = data[:,0]
	counts = data[:,1]
	metadata = extract_metadata(p)
	
	return xr.DataArray(
		data=counts,
		coords={"wavelength": wavelength},
		attrs=metadata,
		name=metadata["name"],
	)

def custom_load(p):
	try: return load_file(p)
	except ValueError:
		warnings.warn(f"Could not load {p}")
		return None

data = [custom_load(p) for p in paths]
data = [d for d in data if d is not None]

# %%
