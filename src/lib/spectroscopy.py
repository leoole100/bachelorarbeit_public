from scipy.signal import lombscargle
from scipy.constants import pi
import emd
import numpy as np

from lib.io import import_spectrum


def calc_thickness(wavelength, intensity, thickness, imf=True):
    """
    Calculate the signal for different thicknesses.

    thickness (np.array): $d n cos \theta2$
    imf (bool): if True, use IMF instead of intensity
    
    Source: 
    A method for measuring and calibrating the thickness of thin films based on infrared interference technology
    """
    if imf:
        imf = emd.sift.sift(intensity)[:,0]
    else:
        imf = intensity
    nu = 1/wavelength
    w = 2*2*thickness * 2*pi
    pgram = lombscargle(nu, imf, w)
    return pgram