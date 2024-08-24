import math
import multiprocessing as mg
import multiprocessing.pool
# import pys2let as ps
import random
import string
import itertools
import os
import jax
jax.config.update("jax_enable_x64", True)
import s2fft
import healpy as hp
import numpy as np
import s2wav
import s2wav
import matplotlib.pyplot as plt
import skyclean
from skyclean import CMB_data

def MW_Map_doubleworker(MW_Pix_Map):
    '''
    Input: MW_Pix_Map: list of mw maps at different scales 
    Each pixel map is a wavelet pixel map of shape (1, Lmax, 2*Lmax-1) (MW sampling, McEwen & Wiaux)
    It is the output of s2wav.analysis
    (Scale: 0, size (1, 4, 7))

    Process:
    1. Covert MW Pixel Map to MW alm space using s2fft.forward

    2. Add zero to the mw alms  
    
    3. Convert mw alm to mw map 
    
    '''
    if MW_Pix_Map.ndim == 3:
        forward_L = MW_Pix_Map.shape[1]
    else:
        forward_L = MW_Pix_Map.shape[0]
    MW_alm = s2fft.forward(MW_Pix_Map, L = forward_L)
    L = MW_alm.shape[0]
    padded_alm = np.zeros((2*L-1,2*(2*L-1)-1),dtype=np.complex128)
    # L = 4 | l = 0,1,2,3 , true lmax is L-1 = 3 | m = -3...0...(L-1)| m = 2(L-1)+1 = 2L-1      
    # double true lmax: 2*3 = 6, and add 1, new L = 7 = 2(L-1)+1 = 2L-1
    # new m = -6...0...(new L-1) | new m = 2*(2L-1)-1
    inner_matrix_middle = MW_alm.shape[1] // 2
    outer_matrix_middle = padded_alm.shape[1] // 2
    start_col = (outer_matrix_middle - inner_matrix_middle)
    end_col = start_col + MW_alm.shape[1] # not included
      
    padded_alm[:MW_alm.shape[0], start_col:end_col] = MW_alm
    # print(padded_alm[:MW_alm.shape[0], start_col:start_col + end_col].shape)
    # print("padded alm size", padded_alm)
    # print(padded_alm.shape)
    
    MW_Pix_Map_doubled = np.real(s2fft.inverse(padded_alm, L = padded_alm.shape[0]))
    # print("Scale:","doubled map size", MW_Pix_Map_doubled.shape)
    # Note
    # assert imaginery part is around zero
    # print(np.imag(MW_Pix_Map_doubled))
    # MW_Pix_Map_doubled = s2fft.inverse(MW_alm_doubled, L = MW_alm_doubled.shape[0])
    
    return MW_Pix_Map_doubled


def smoothed_covariance(MW_Map1, MW_Map2):
    """
    Compute a smoothed covariance map between two multi-frequency wavelet pixel maps.

    This function takes in two wavelet-transformed maps (`MW_Map1` and `MW_Map2`), 
    which are complex-valued arrays of the same size representing wavelet coefficients 
    at different frequencies. It calculates the covariance between these two maps, 
    smooths the result in harmonic space using a Gaussian beam, and then returns 
    the smoothed covariance map.

    Parameters:
    -----------
    MW_Map1 : ndarray
        A complex-valued array representing the wavelet-transformed pixel map at 
        a certain frequency. Should be of the same size as `MW_Map2`.
    
    MW_Map2 : ndarray
        A complex-valued array representing the wavelet-transformed pixel map at 
        a different frequency. Should be of the same size as `MW_Map1`.

    Returns:
    --------
    R_covariance_map : ndarray
        A real-valued array representing the smoothed covariance map between 
        `MW_Map1` and `MW_Map2`.

    Notes:
    ------
    - The function first computes the covariance of the real parts of the input maps.
    - The covariance map is then transformed into harmonic space for efficient smoothing.
    - A Gaussian beam is applied in harmonic space to achieve the smoothing effect.
    - Finally, the smoothed map is transformed back to real space and returned.

    Example:
    --------
    R_map = smoothed_covariance(MW_Map1, MW_Map2)
    """
    smoothing_lmax = MW_Map1.shape[0]
    # Get the real part of the map
    map1 = np.real(MW_Map1)
    map2 = np.real(MW_Map2)
    # Covariance matrix
    R_MW_Pixel_map = np.multiply(map1, map2) + 0.j  # Add back in zero imaginary part

    # Smoothing in harmonic space for efficiency
    R_MW_alm = s2fft.forward(R_MW_Pixel_map, L=smoothing_lmax)

    nsamp = 1200.0
    lmax_at_scale_j = R_MW_alm.shape[0]
    npix = hp.nside2npix(1 << (int(0.5 * lmax_at_scale_j) - 1).bit_length())
    scale_fwhm = 4.0 * math.sqrt(nsamp / npix)

    gauss_smooth = hp.gauss_beam(scale_fwhm, lmax=smoothing_lmax - 1)
    MW_alm_beam_convolved = np.zeros(R_MW_alm.shape, dtype=np.complex128)

    # Convolve the MW alms with the beam
    for i in range(R_MW_alm.shape[1]):
        MW_alm_beam_convolved[:, i] = R_MW_alm[:, i] * gauss_smooth

    R_covariance_map = np.real(s2fft.inverse(MW_alm_beam_convolved, L=smoothing_lmax))

    return R_covariance_map
