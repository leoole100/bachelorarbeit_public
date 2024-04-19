"""
Module for reading experimental files.
"""
from math import e
import os
import attr
import numpy as np
import re
import h5py
import csv
import xarray as xr

def _read_csv(path):
	rows = []
	with open(path) as f:
		r = csv.reader(f, delimiter="\t")
		for row in r:
			if len(row) == 0:
				return rows
			rows.append(row)
	return rows

def import_spectrum(p:str):
	"""
	Import a spectrum from a csv file.   
	Assumes that the first column is wavelength in nm and the second column is the intensity.   
	"""
	d = np.array(_read_csv(p))[:, :2]
	# convert strings to floats
	d = d.astype(float)

	ar = xr.DataArray(
		d[:, 1],
		coords={
			'wavelength': d[:, 0]
		}
	)

	# get the metadata
	try:
		number, exposure = p.replace(".", "_").split("s")[0].split("_")[-1].split("x")
		number = int(number)
		exposure = float(exposure)
		ar /= number * exposure
	except:
		number = np.nan
		exposure = np.nan

	ar.attrs = {
		**ar.attrs,
		"path": p.split("data/")[-1],
		"name": p.split("data/")[-1].split(".")[0],
		"number": number,
		"exposure": exposure,
		"type": "spectrum"
	}
	ar.name = ar.attrs["name"]
	
	return ar

def import_scan(p):
	with h5py.File(p, "r") as f:
		field = np.array(f["data_full"]["magnet"]["field"])
		wavelength = np.array(f["x"])
		counts = np.array(f["z"])
		angle = np.array(f["data_full"]["apt"][
			list(f["data_full"]["apt"].keys())[0]
		]["position"])

		exposure = f["data_full"]["spectrometer"]["exposure"][0]
		number = f["data_full"]["spectrometer"]["number"][0]

		counts = counts / number / exposure

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
		"multiple_fields": multiple_fields,
		"exposure": exposure,
		"number": number,
		"type": "scan"
	}
	ar.name = ar.attrs["name"]


	diff_field = np.diff(ar.field)
	if np.all(diff_field > 0):
		ar.attrs["field_direction"] = 1.
	elif np.all(diff_field < 0):
		ar.attrs["field_direction"] = -1.
	else:
		ar.attrs["field_direction"] = np.nan

	return ar

def import_custom_scan(p):
	with h5py.File(p, "r") as f:
		angle_count = len(np.unique(f['apt_angle']))

		if "magnet_field" in f:
			field = f["magnet_field"][::angle_count]
		else:
			field = np.array([np.nan])

		angle = f["apt_angle"][:angle_count]
		wavelength = f["wavelength"][0]
		counts = f["counts"][:].reshape(field.shape[0], angle.shape[0], wavelength.shape[0])

		time = f["time"][:].reshape(field.shape[0], angle.shape[0])

		if "temperature" in f:
			temperature = f["temperature"][:].reshape(field.shape[0], angle.shape[0])
		else:
			temperature = np.full_like(time, np.nan)

		if "position" in f:
			position = f["position"][:].reshape(field.shape[0], angle.shape[0], 3)
		else:
			position = np.full_like(counts, np.nan)

		exposure = f["data_full"]["spectrometer"]["exposure"][0]
		number = f["data_full"]["spectrometer"]["number"][0]

	ar = xr.DataArray(
		counts,
		dims=["field", "angle", "wavelength"],
		coords={
			"field": field,
			"angle": angle,
			"wavelength": wavelength,
		},
		attrs={
			"exposure": exposure,
			"number": number,
			"type": "custom scan"
		}
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

import matplotlib.image as mpimg
def import_image(p):
	"""Import an image from a file."""
	img = mpimg.imread(p)
	
	if len(img.shape) == 3:
		coords = {
			"x": np.arange(img.shape[0]),
			"y": np.arange(img.shape[1]),
			"channel": np.arange(img.shape[2])
		}
	else:
		coords = {
			"x": np.arange(img.shape[0]),
			"y": np.arange(img.shape[1])
		}
 
	return xr.DataArray(
		img,
		coords=coords,
		attrs={
			"type": "image",
		}
	) 

def import_file(p):
	"""tries all import methods"""
	try: d = import_spectrum(p)
	except: 
		try: d = import_scan(p)
		except:  
			try: d = import_custom_scan(p)
			except: 
				try: d = import_image(p)
				except: 
					return None

	d.attrs["name"] = p.split("/")[-1].split(".")[0]
	d.name = d.attrs["name"]
	d.attrs["path"] = p
	return d