"""
This module contains function to read the maps from pylums.
"""
import numpy as np

def estimate_step(sel):
    """
    Estimate the step size of the map.

    Parameters
    ----------
    sel(pd.Series): a measurement
    """
    return np.unique(sel.y, return_counts=True)[1][0]