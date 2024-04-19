"""
This preamble is intended to be imported as ```from lib.preamble import *```
in jupyter notebooks.
It will import common libraries and set up matplotlib.
Also, it will import all functions from this library.
"""

# import libraries
import numpy as np, pandas as pd, xarray as xr, scipy as sp
import matplotlib.pyplot as plt, matplotlib as mpl, seaborn as sns
from glob import glob
import os
from types import *
from itertools import *
from functools import *
from operator import *
from more_itertools import *
import re
from pprint import pprint
import h5py

# often used functions
from scipy.interpolate import interp1d
import typing

# import all functions from this library
from .io import *
from .utils import *
import lib.plot as plot
from .spectroscopy import *
from .map import *
from .polarisation import *
from .metadata import *
import lib

# set up matplotlib
import colorcet as cc

import scienceplots
mpl.rcdefaults()
plt.style.use(['science','nature'])


# Define Colors
SEEBLAU = '#00A9E0'
SEEGRAU = '#9AA0A7'
SEEBLAU_LIST = ['#CCEEF9', '#A6E1F4', '#59C7EB', '#00A9E0', '#008ECE']

FIGURE_RATION =  1.5
FIGSIZE_SMALL = (2.5, 2.5/FIGURE_RATION)
FIGSIZE_MEDIUM = (3.5, 3.5/FIGURE_RATION)
FIGSIZE_LARGE = (5, 5/FIGURE_RATION)
FIGSIZE_HUGE = (6, 6/FIGURE_RATION)
FIGSIZE_WIDE = (7, 7/2/FIGURE_RATION)

plt.rcParams.update({
	'savefig.dpi': 300,
	'figure.dpi': 150,
	'figure.figsize': FIGSIZE_LARGE,
	'figure.autolayout': True,
})

FONTSIZE = 10
FONTSIZE_SMALL = 9
FONTSIZE_TINY = 8
plt.rc('font', size=FONTSIZE)
plt.rc('axes', titlesize=FONTSIZE)
plt.rc('axes', labelsize=FONTSIZE)
plt.rc('xtick', labelsize=FONTSIZE_SMALL)
plt.rc('ytick', labelsize=FONTSIZE_SMALL)
plt.rc('legend', fontsize=FONTSIZE)
plt.rc('figure', titlesize=FONTSIZE_SMALL)
plt.rcParams['figure.titlesize'] = FONTSIZE_TINY
plt.rcParams['axes.labelpad'] = 2
plt.rcParams['axes.labelsize'] = FONTSIZE_SMALL


# disable the use of latex
plt.rcParams['text.usetex'] = False

# set latex preamble to load font
# plt.rcParams['text.latex.preamble'] = r'\usepackage{arimo}'

# set the fonts for the figure
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = ['Fira Sans', 'Arimo', 'Roboto', 'Liberation Sans', 'sans-serif']
plt.rcParams['font.sans-serif'] = 'Roboto Regular'


plt.rcParams['errorbar.capsize'] = 3

# do classic legend
plt.rcParams['legend.frameon'] = False
# plt.rcParams['legend.numpoints'] = 2
# plt.rcParams['legend.framealpha'] = None
# plt.rcParams['legend.scatterpoints'] = 3
plt.rcParams['legend.edgecolor'] = 'inherit'
plt.rcParams['axes.autolimit_mode'] = 'data' # 'data', 'round_numbers'

# make border and axis ticks gray
plt.rcParams['axes.edgecolor'] = SEEGRAU
plt.rcParams['xtick.color'] = SEEGRAU
plt.rcParams['ytick.color'] = SEEGRAU
plt.rcParams['xtick.labelcolor'] = 'black'
plt.rcParams['ytick.labelcolor'] = 'black'

# setup grid
plt.rcParams['axes.grid'] = False
plt.rcParams['grid.color'] = SEEGRAU
plt.rcParams['grid.linewidth'] = 0.5


from colorcet import cm
# CMAP = cm["CET_L8"]
CMAP = "magma"
CMAP_CYCLIC = cm["CET_C6s"]

# set default color map 
plt.rcParams['image.cmap'] = CMAP


plt.rcParams['axes.prop_cycle'] = plt.cycler(color=
[(0.0, 0.6627450980392157, 0.8784313725490196),
 (0.6039215686274509, 0.6274509803921569, 0.6549019607843137),
 (0.24313725490196078, 0.32941176470588235, 0.5882352941176471),
 (0.5568627450980392, 0.12549019607843137, 0.2627450980392157),
 (0.8784313725490196, 0.3764705882352941, 0.49411764705882355),
 (0.996078431372549, 0.6274509803921569, 0.5647058823529412),
 (0.0392156862745098, 0.5647058823529412, 0.5254901960784314),
 (0.027450980392156862, 0.44313725490196076, 0.5294117647058824)]
)