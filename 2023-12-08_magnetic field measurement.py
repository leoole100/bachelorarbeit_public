# %%
from tkinter import font
from lib.preamble import *

import warnings
# warnings.filterwarnings("ignore")

def cos_sqr(x, *p):
	return p[0] * np.cos((x-p[1]) * np.pi / 180 ) ** 2 + p[2]

def polarisation(angle, intens):
	p0 = [intens.max() - intens.min(), 90, intens.min()]
	popt, pcov = sp.optimize.curve_fit(cos_sqr, angle, intens, p0=p0)
	polarisation = np.abs(popt[0] / (popt[0] + popt[2]))
	pol_angle = popt[1]%90
	return (polarisation, pol_angle)

def polarisation_xarray(d):
	pol, angle = xr.apply_ufunc(
		polarisation,
		d.angle,
		d,
		input_core_dims=[["angle"], ["angle"]],
		output_core_dims=[[], []],
		vectorize=True,
		dask="parallelized",
		output_dtypes=[float, float]
	)

	return xr.Dataset(
		{
			"polarisation": pol,
			"angle": angle,
		},
		coords={
			"field": d.field,
			"wavelength": d.wavelength,
		},
		attrs=d.attrs,
	)

data = []

# %% import backgrounds
paths = glob("../data/2023-12-05*/d*.asc")
paths += glob("../data/2023-12-06*/d*.asc")
paths += glob("../data/2023-12-07*/d*.asc")
paths = [p for p in paths if "bkg" in p]
paths.sort()

import csv
from curses import raw

def _read_csv(path):
	rows = []
	with open(path) as f:
		r = csv.reader(f, delimiter="\t")
		for row in r:
			if len(row) == 0:
				return rows
			rows.append(row)
	return rows

def import_files(p):
	d = np.array(_read_csv(p))[:, :-1]
	# convert strings to floats
	d = d.astype(float)

	ar = xr.DataArray(
		d[:, 1],
		coords={
			'wavelength': d[:, 0]
		}
	)

	ar.attrs = {
		**ar.attrs,
		"path": p.split("data/")[-1],
		"name": p.split("data/")[-1].split(".")[0],
	}
	ar.name = ar.attrs["name"]
	
	return ar

bkg = [import_files(p) for p in paths]

bkg[0] = bkg[0] / 3
bkg[1] = bkg[1] / 3

import difflib

def background_substract(sel, b=None):
	if b is None:		
		same_folder = [b for b in bkg if sel.name.split("/")[0] in b.name]
		if len(same_folder) == 1: b=same_folder[0]
		elif len(same_folder) > 1:
			b_name = difflib.get_close_matches(sel, [b.name for b in same_folder], n=1, cutoff=0)[0]
			b = [b for b in same_folder if b.name == b_name][0]
		else:
			before = [b for b in bkg if b.name < sel.name]
			if before:
				b = sorted(before, key=lambda x: x.name)[-1]
			else:
				b = sorted(bkg, key=lambda x: x.name)[0]
	
	d =  sel - b.interp(wavelength=sel.wavelength, kwargs={"fill_value": "extrapolate"})
	d.attrs = sel.attrs
	d.name = sel.name
	d.attrs["background"] = b
	return d

[b.name for b in bkg]

# %% import with normal scanning script
from enum import unique
import h5py

paths = glob("../data/2023-12-05*/*hd5.h5")
paths += glob("../data/2023-12-06*/*hd5.h5")
paths.sort()

def import_files(p):
	try:
		with h5py.File(p, "r") as f:
			field = np.array(f["data_full"]["magnet"]["field"])
			wavelength = np.array(f["x"])
			counts = np.array(f["z"])
			angle = np.array(f["data_full"]["apt"][
				list(f["data_full"]["apt"].keys())[0]
			]["position"])
	except:
		print(f"Error importing:\t{p}")
		return None

	unique_angles = np.unique(angle)
	counts = counts.reshape(field.shape[0]//len(unique_angles), len(unique_angles), -1)
	field = field[::len(unique_angles)]

	multiple_fields = (field.shape[0] == 1)

	ar = xr.DataArray(
		counts,
		coords={
			"field": field,
			"angle": unique_angles,
			"wavelength": wavelength[0],
		},
	)
	ar.attrs = {
		**ar.attrs,
		"path": p.split("data/")[-1],
		"name": ".".join(p.split("data/")[-1].split(".")[:-1]),
		"multiple_fields": multiple_fields,
	}
	ar.name = ar.attrs["name"]
	
	return ar

data_import = [import_files(p) for p in paths]
data_import = [background_substract(d) for d in data_import if d is not None]
data = [d for d in data if d.name not in [d.name for d in data_import]]
data += data_import

{i: d.name for i, d in enumerate(data)}

# %%  import all with custom script
import h5py

paths = glob("../data/2023-12-05*/*hd5.h5")
paths += glob("../data/2023-12-06*/*.h5")
paths += glob("../data/2023-12-07*/*.h5")
paths += glob("../data/2023-12-08*/*.h5")
paths.sort()

paths = list(filter(lambda p: "hd5" not in p, paths))

def import_custom_script(p):
	with h5py.File(p, "r") as f:
		angle_count = len(np.unique(f['apt_angle']))

		field = f["magnet_field"][::angle_count]
		angle = f["apt_angle"][:angle_count]
		wavelength = f["wavelength"][0]
		counts = f["counts"][:].reshape(field.shape[0], angle.shape[0], wavelength.shape[0])

		time = f["time"][:].reshape(field.shape[0], angle.shape[0])
		temperature = f["temperature"][:].reshape(field.shape[0], angle.shape[0])
		position = f["position"][:].reshape(field.shape[0], angle.shape[0], 3)

	ar = xr.DataArray(
		counts,
		dims=["field", "angle", "wavelength"],
		coords={
			"field": field,
			"angle": angle,
			"wavelength": wavelength,
		},
	)

	# add coord time
	ar.coords["time"] = (
		["field", "angle"],
		time
	)

	# add coord temperature
	ar.coords["temperature"] = (
		["field", "angle"],
		temperature
	)

	return ar

def import_files(p):

	# try:
	ar = import_custom_script(p)
	# except:
		# print(f"Error importing:\t{p}")
		# return None

	# if ar is None:
		# return None
	
	ar.attrs = {
		**ar.attrs,
		"path": p.split("data/")[-1],
		"name": ".".join(p.split("data/")[-1].split(".")[:-1]),
	}
	ar.name = ar.attrs["name"]

	return ar

data_import = [import_files(p) for p in paths]
data_import = [background_substract(d) for d in data_import if d is not None]
data = [d for d in data if d.name not in [d.name for d in data_import]]
data += data_import

{i: d.name for i, d in enumerate(data)}

# %%
plt.figure(figsize=FIGSIZE_WIDE)

def amplitude(d):
	return np.sqrt(d.sel(angle=0, method="nearest")**2 + d.sel(angle=45, method="nearest")**2)

for d in [
	data[1],
	data[2],
	data[4],
	data[9]
]:
	reduced = amplitude(d).mean("wavelength")
	(
		reduced/reduced.sel(field=0)
	).plot(
		label=d.name.replace("/", "\n"),
		linestyle="--",
	)
# also plot the hysteresis measurement
reduced = amplitude(data[12]).mean("wavelength")
(
	reduced/reduced.min("field")
).plot(
	label=data[12].name.replace("/", "\n"),
)
plt.legend(
	fontsize=FONTSIZE_TINY,
	bbox_to_anchor=(1., 1.01),
)
plt.ylabel("Unpolarised PL")
plt.savefig("../figures/2023-12-08 Different Measurements.png")
plt.show()

# %%
plt.figure(figsize=FIGSIZE_WIDE)
for d in [
	data[1],
	data[2],
	data[4],
	data[9]
]:
	reduced = amplitude(d).mean("wavelength")
	(
		np.abs(reduced/reduced.sel(field=0)-1)
	).plot(
		label=d.name.replace("/", "\n"),
		linestyle="--",
	)

# also plot the hysteresis measurement
reduced = amplitude(data[12]).mean("wavelength")
(
	np.abs(reduced/reduced.min("field")-1)
).plot(
	label=data[12].name.replace("/", "\n"),
)

plt.legend(
	fontsize=FONTSIZE_TINY,
	bbox_to_anchor=(1., 1.01),
)
plt.ylabel("")
plt.savefig("../figures/2023-12-08 Different Measurements Aligned.png")
plt.show()

# %%
sel = data[-1] # nice splitting
# sel = data[4] # nice splitting
# sel = data[6] # nice splitting
# sel = data[-1]
# wavelength_slice = slice(None, None)
wavelength_slice = slice(837, 843)
# wavelength_slice = slice(838.8, 840.9)
sel = sel.where(~np.isnan(sel), drop=True)
angles = sel.angle
# sel = sel / sel.rolling(wavelength=15).mean().max(["wavelength", "angle"])
sel = sel.rolling(wavelength=3).mean()
sel = sel.sel(wavelength=wavelength_slice)

sel = sel.sortby("field")

fig, axs = plt.subplots(1, len(angles), sharex=True, sharey=True, figsize=FIGSIZE_WIDE)
fig.suptitle(sel.name)
for ang, ax in zip(angles, axs):
	img = sel.sel(angle=ang).plot(
		ax=ax, 
		cmap=cm["CET_L8"],
		vmin=sel.min(),
		vmax=sel.max(),
		# levels=20,
		add_colorbar=False
	)
	# ax.set_title("")
	ax.set_xlabel("")
	ax.set_ylabel("")

for ax in axs[1:]:
	ax.set_ylabel("")

# plt.colorbar(img)

fig.supxlabel("Wavelength (nm)")
fig.supylabel("Field (T)")
# plt.savefig(f"../figures/2023-12-06_{sel.name.replace('/', '_')}.png")
plt.show()

# %%
plt.figure()
# plot with categorical axis
sel.mean(["angle"]).max("wavelength").plot.line(x="field", label="840")
plt.suptitle(sel.name)
plt.ylabel("PL")
plt.show()

# %%
sel = data[i_sel]
wavelength_slice = slice(838.8, 840.9)
# wavelength_slice = slice(None, None)
sel = sel.where(~np.isnan(sel), drop=True)
angles = sel.angle
fields = sel.field
# sel = sel / sel.mean(dim="wavelength")
sel = sel.rolling(wavelength=10).mean()
sel = sel.sel(wavelength=wavelength_slice)
# sel = sel/sel.max(["wavelength", "angle"])

fig, axs = plt.subplots(1, len(angles), figsize=FIGSIZE_WIDE, sharex=True, sharey=True)
plt.suptitle(sel.name)
colors = plt.get_cmap("magma")(fields / fields.max() / 1.2)

for a, ax in zip(angles, axs):
	sel_sub = sel.sel(
		wavelength=wavelength_slice,
		angle=a,
	)
	for f, c in zip(fields, colors):
		sel_sub.sel(field=f).plot(label=f"{float(f)} T", ax=ax, color=c)
	ax.set_xlabel("")
	ax.set_ylabel("")
	ax.set_title(f"angle={float(a)}")

for ax in axs[1:]:
	ax.set_ylabel("")

# plt.legend()
# add a color bar with field
plt.show()

# %%
%%time
sel = data[i_sel]
# wavelength_slice = slice(838.8, 840.9)
wavelength_slice = slice(838, 841.5)
sel = sel.where(~np.isnan(sel), drop=True)
angles = sel.angle
sel = sel.rolling(wavelength=3).mean()
sel = sel.sel(wavelength=wavelength_slice)
pol = polarisation_xarray(sel.assign_coords(angle=2*sel.angle), fast=False)

# %%
pol = pol.sortby("field")

fig = plt.figure(figsize=FIGSIZE_WIDE)
plt.suptitle(sel.name)
# plt.subplot(131)
# img = sel.sel(angle=0).plot(
# 	add_labels=False, 
# 	add_colorbar=False,
# 	cmap="magma",
# )
# plt.colorbar(img)
# plt.title(r"PL ($\parallel H$)")

plt.subplot(131)
img = sel.sortby("field").mean("angle").plot(
	add_labels=False, 
	add_colorbar=False,
	cmap=cm["CET_L8"],
)
plt.colorbar(img)
plt.title(r"PL all Polarisations")

plt.subplot(132)
pol.polarisation.plot(
	vmin=0,
	add_labels=False,
	cmap=cm["CET_L8"],
)
plt.title("Polarisation")

plt.subplot(133)
(
	pol.angle
).plot(
	# vmin=0, vmax=90,
	cmap=cm["CET_C7s"],
	add_labels=False
)
plt.title("Polarisation angle")

fig.supxlabel("Wavelength (nm)")
fig.supylabel("Field (T)")

plt.savefig(f"../figures/2023-12-06_polarisation_{sel.name.replace('/', '_')}.png")
plt.show()

# %%
plt.figure()
# sel.sel(wavelength=wavelength_slice).mean("wavelength").mean("angle").plot()


wavelength_max = sel.mean(["field", "angle"]).idxmax("wavelength")
pol.polarisation.sel(
	wavelength=slice(wavelength_max-1, wavelength_max+1)
).mean("wavelength").plot(
	label="max intensity",
)

plt.legend()
plt.suptitle(sel.name)
plt.title("")
plt.show()

# %%



