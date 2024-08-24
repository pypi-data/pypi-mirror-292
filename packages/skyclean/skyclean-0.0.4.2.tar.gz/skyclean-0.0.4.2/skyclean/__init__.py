# from .CMB_data import cmb_data
from skyclean.CMB_data import CMB_Data
# from .tools.useful_functions import arcmin_to_radians
from skyclean.tools.useful_functions import arcmin_to_radians, download_cmb_realizations
from skyclean.tools.map_functions import beam_deconvolution, reduce_hp_map_resolution, hp_alm_2_mw_alm, mw_alm_2_hp_alm, hp_fits_map_to_MW_map, visualize_MW_Pix_map
from skyclean.tools.wavelets_functions import wavelet_transform, save_wavelet_scaling_coeffs, load_wavelet_scaling_coeffs
from skyclean.tools.ILC_functions import MW_Map_doubleworker, smoothed_covariance

# print(type(CMB_Data()))


