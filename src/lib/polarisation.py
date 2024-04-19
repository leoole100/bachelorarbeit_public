import numpy as np
import scipy as sp
import xarray as xr
import numba as nb
from sklearn.linear_model import HuberRegressor, LinearRegression

# define polarisation
def cos_sqr(x, A, phi, B):
	return np.abs(A) * np.cos((x-phi) * np.pi / 180 ) ** 2 + np.abs(B)

def fit_cos_sqr(angle, intens, p0=None, fast=True, **kwargs):
	if fast:
		return fit_linear(angle, intens, p0=p0, **kwargs)
	if p0 is None:
		p0 = [intens.max() - intens.min(), 90, intens.min()]
	popt, pcov = sp.optimize.curve_fit(cos_sqr, angle, intens, 
		p0=p0,
		bounds=(
			[0, -np.inf, 0],
			[np.inf, np.inf, np.inf]
		)
	)
	return popt, pcov


def fit_linear(angle, intens, p0=None, robust=False, drift=False):
	if p0 is None:
		p0 = [intens.max() - intens.min(), 0]
	if robust: reg = HuberRegressor()
	else: reg = LinearRegression()
 
	x = np.cos(angle * np.pi / 180 * 2)	# *2 because of the cos^2
	y = np.sin(angle * np.pi / 180 * 2)	# *2 because of the cos^2
 
	if drift:
		z = np.arange(len(angle))
		X = np.vstack([x, y, z]).T
	else:
		X = np.vstack([x, y]).T
	reg.fit(X, intens)
 
	A = 2*np.sqrt(reg.coef_[0]**2 + reg.coef_[1]**2)
	phi = np.arctan2(reg.coef_[1], reg.coef_[0]) * 180 / np.pi
	phi = phi / 2  # because of the cos^2
	B = reg.intercept_ - A/2
 
	return (A, phi, B), None
	 

def polarisation_degree(popt):
	return np.abs(popt[0] / (popt[0] + 2*popt[2]))

def polarisation(angle, intens):
	try:
		popt, _ = fit_cos_sqr(angle, intens)
		polarisation = polarisation_degree(popt)

		return (polarisation, popt[1] % 180)
	except:
		return (np.nan, np.nan)

def polarisation_xarray(d, uncertainties=True):
	pol, angle = xr.apply_ufunc(
		polarisation,
		d.angle,
		d,
		input_core_dims=[["angle"], ["angle"]],
		output_core_dims=[[], []],
		vectorize=True,
		dask="parallelized",
		output_dtypes=[float, float, float]
	)

	return xr.Dataset(
		{
			"polarisation": pol,
			"angle": angle
		},
		coords= d.drop_vars('angle').coords,
		attrs=d.attrs,
	)
 
def polarisation_binned(sel, **kwargs):
	"""
	bins along kwargs key axis into value bins
	"""
	axis, bins = kwargs.popitem()
	assert axis in sel.dims, f"axis {axis} not in dims {sel.dims}"
	sel = sel.coarsen(wavelength=sel.coords[axis].shape[0]//bins, boundary="trim").mean()
	pol = polarisation_xarray(sel.assign_coords(angle=2*sel.angle))
	return pol

def unploarized(d: xr.DataArray):
	"""
	returns what the Pl would be without a polarizer
	even, if the angle is not sampled evenly
	"""
	...
	return d.sel(angle=[0, 45], method="nearest", tolerance=1).mean('angle')


def monotonic_sections_axis(d: xr.DataArray, axis):
	"""
	returns all sections of the xarray where the axis is changing monotonically
	"""
	# find all sections where the axis is monotonic
	diff = np.sign(np.diff(d[axis]))
	# find the sign changes
	sign_change = np.diff(diff)
	sign_change = np.where(sign_change != 0)[0]

	# split the xarray at the sign changes
	sections = []
	beginning = 0
	for i in sign_change:
		sections.append(d.isel(**{axis: slice(beginning, i+2)}))
		beginning = i+1
	sections.append(d.isel(**{axis: slice(beginning, None)}))

	return sections


def dichroism(d):
	return (d.isel(angle=0) - d.isel(angle=1)) / (d.isel(angle=0) + d.isel(angle=1))