from __future__ import print_function
import numpy as np
# import scipy as sp
# from scipy import interpolate

import script
import script_fortran_modules


def create_light_cone_map(z_arr, field_z_arr, box, ngrid, omega_m, omega_l, vlos_z_arr=None):

    nk = script_fortran_modules.ionization_map.los_array_size(z_arr[-1], z_arr[0], box, ngrid, omega_m, omega_l)
    if (vlos_z_arr is None):
        add_rsd = False
    else:
        add_rsd = True
    field_los_arr, xcom_los_arr, zlos_arr = script_fortran_modules.ionization_map.create_lightcone_map(z_arr, box, field_z_arr, vlos_z_arr, omega_m, omega_l, add_rsd, nk)

    return field_los_arr, xcom_los_arr, zlos_arr

    
def get_tau(z_arr, QHII_arr, omega_m, omega_l, omega_b, h, YHe):
    
    if (QHII_arr.ndim == 1):
        tau_arr = script_fortran_modules.ionization_map.tau_arr(z_arr, QHII_arr, omega_m, omega_l, omega_b, h, YHe)
    elif (QHII_arr.ndim == 4):
        tau_arr = script_fortran_modules.ionization_map.get_tau_grid_arr(z_arr, QHII_arr, omega_m, omega_l, omega_b, h, YHe)

    return tau_arr

def create_zeta_fcoll_from_halo_catalogue(zeta, densitycontr_arr, mhalo_arr, xhalo_arr, box, omega_m, h, log10Mmin=-np.inf, log10Mmax=np.inf):
    ## mhalo_arr and log10Mmin, log10Mmax should be in Msun
    ## box in Mpc / h

    ngrid = np.shape(densitycontr_arr)[0]
    log10mhalo_arr = np.log10(mhalo_arr)
    mask_halo = np.logical_and(log10mhalo_arr >= log10Mmin, log10mhalo_arr <= log10Mmax)
    if (len(mhalo_arr[mask_halo]) == 0):
        return np.zeros_like(densitycontr_arr)


    if (callable(zeta)):
        zeta_halo_density_field_arr = script_fortran_modules.matter_fields_haloes.smooth_halo_field_cic(xhalo_arr[:,mask_halo], zeta(mhalo_arr[mask_halo]) * mhalo_arr[mask_halo], box, ngrid) ### Msun
    else:
        zeta_halo_density_field_arr = zeta * script_fortran_modules.matter_fields_haloes.smooth_halo_field_cic(xhalo_arr[:,mask_halo], mhalo_arr[mask_halo], box, ngrid) ### Msun
    

    rho_c_by_hsq = 2.7755e11
    total_density_field_arr = (1 + densitycontr_arr) * (omega_m / h) * rho_c_by_hsq * box ** 3 / ngrid ** 3 ### Msun
    ### omega_m * (rho_c_by_hsq * h ** 2) * (box / h) ** 3
    zeta_fcoll_arr = np.zeros_like(zeta_halo_density_field_arr)
    mask = total_density_field_arr > 0.0
    zeta_fcoll_arr[mask] = zeta_halo_density_field_arr[mask] / total_density_field_arr[mask]
    
    return zeta_fcoll_arr

def read_density_velocity_standard(filename):

    ngrid = script_fortran_modules.matter_fields.density_array_size(filename)
    densitycontr_arr, velocity_arr, box, z, omega_m, omega_l, h = script_fortran_modules.matter_fields.read_density_contrast_velocity(filename, ngrid)
    return densitycontr_arr, velocity_arr, box, z, omega_m, omega_l, h

def write_density_velocity_standard(filename, densitycontr_arr, velocity_arr, box, z, omega_m, omega_l, h):

    script_fortran_modules.matter_fields.write_density_velocity(filename, 
                                                                densitycontr_arr, velocity_arr, 
                                                                box, z, omega_m, omega_l, h)

def make_density_velocity_field_from_gadget_snapshot(gadget_snap, outpath='/tmp/', sigma_8=0.829, ns=0.961, omega_b=0.0482, scaledist=1.e-3, dx=1.0):

    default_simulation_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=0.829, ns=0.961, omega_b=0.0482, scaledist=scaledist, default_dx=dx)
    

    pos_arr, vel_arr = script_fortran_modules.matter_fields.read_gadget_dm_pos_vel(default_simulation_data.snapshot_file, default_simulation_data.npart, default_simulation_data.scaledist)

    densitycontr_arr, velocity_arr = script_fortran_modules.matter_fields.smooth_density_velocity_cic(pos_arr, vel_arr, default_simulation_data.box, default_simulation_data.default_ngrid)

    delta_mean = np.mean(densitycontr_arr)
    densitycontr_arr = densitycontr_arr / delta_mean - 1
    
    return densitycontr_arr, velocity_arr, default_simulation_data.box, default_simulation_data.z, default_simulation_data.cosmo.omega_m, default_simulation_data.cosmo.omega_l, default_simulation_data.cosmo.h

def compute_powspec(input_arr, box, nbins=20, kmin=None, kmax=None, log_bins=False, convolve=False, bin_weight=False):

    ngrid = np.shape(input_arr)[0]
    FFTW_ESTIMATE = 64
    FFTW_IFINV = 1
    plan, kfft = script_fortran_modules.powspec.initialize_plan(ngrid, FFTW_IFINV, FFTW_ESTIMATE, box)
    kmag = script_fortran_modules.powspec.get_kmag(kfft)

    if (kmin is None): kmin = 2 * np.pi / box
    if (kmax is None): kmax = np.pi * ngrid / box

    if (kmax <= kmin): sys.exit('set_k_bins: kmax is less than kmin')

    if (log_bins):
        if (nbins < 2):
            dlnk = 0.1
            nbins = int( (np.log(kmax) - np.log(kmin)) / dlnk )
        else:
            dlnk = (np.log(kmax) - np.log(kmin)) / (nbins)
            lnk_edges = np.linspace(np.log(kmin), np.log(kmax), num=nbins+1, endpoint=True)
            lnk_bins = (lnk_edges[:-1] + lnk_edges[1:]) / 2
            k_edges = np.exp(lnk_edges)
            k_bins = np.exp(lnk_bins)
    else:
        if (nbins < 2):
            dk = kmin
            nbins = int(self.ngrid / 2) - 1
        else:
            dk = (kmax - kmin) / (nbins)
            k_edges = np.linspace(kmin, kmax, num=nbins+1, endpoint=True)
            k_bins = (k_edges[:-1] + k_edges[1:]) / 2

    powspec_arr = script_fortran_modules.powspec.compute_powspec(plan, input_arr, box, convolve)
    powspec_binned, kount, k_bins_2 = script_fortran_modules.powspec.bin_powspec(k_edges, kmag, powspec_arr)
    if (bin_weight): k_bins = k_bins_2
    return k_bins, powspec_binned, kount


def compute_cross_powspec(input_arr1, input_arr2, box, nbins=20, kmin=None, kmax=None, log_bins=False, convolve=False, bin_weight=False):

    ngrid = np.shape(input_arr1)[0]
    FFTW_ESTIMATE = 64
    FFTW_IFINV = 1
    plan, kfft = script_fortran_modules.powspec.initialize_plan(ngrid, FFTW_IFINV, FFTW_ESTIMATE, box)
    kmag = script_fortran_modules.powspec.get_kmag(kfft)

    if (kmin is None): kmin = 2 * np.pi / box
    if (kmax is None): kmax = np.pi * ngrid / box

    if (kmax <= kmin): sys.exit('set_k_bins: kmax is less than kmin')

    if (log_bins):
        if (nbins < 2):
            dlnk = 0.1
            nbins = int( (np.log(kmax) - np.log(kmin)) / dlnk )
        else:
            dlnk = (np.log(kmax) - np.log(kmin)) / (nbins)
            lnk_edges = np.linspace(np.log(kmin), np.log(kmax), num=nbins+1, endpoint=True)
            lnk_bins = (lnk_edges[:-1] + lnk_edges[1:]) / 2
            k_edges = np.exp(lnk_edges)
            k_bins = np.exp(lnk_bins)
    else:
        if (nbins < 2):
            dk = kmin
            nbins = int(self.ngrid / 2) - 1
        else:
            dk = (kmax - kmin) / (nbins)
            k_edges = np.linspace(kmin, kmax, num=nbins+1, endpoint=True)
            k_bins = (k_edges[:-1] + k_edges[1:]) / 2

    powspec_arr = script_fortran_modules.powspec.compute_cross_powspec(plan, input_arr1, input_arr2, box, convolve)
    powspec_binned, kount, k_bins_2 = script_fortran_modules.powspec.bin_powspec(k_edges, kmag, powspec_arr)
    if (bin_weight): k_bins = k_bins_2
    return k_bins, powspec_binned, kount

def get_Dl_kSZ_patchy(z_arr, Pqperp_binned_z_arr, tau_arr, l_edges, omega_m, omega_l, omega_b, YHe, h):
    
    Cl_kSZ = script_fortran_modules.ionization_map.get_cl_ksz_patchy(z_arr, Pqperp_binned_z_arr, tau_arr, omega_m, omega_l, omega_b, YHe, h)
    l_bins = (l_edges[:-1:] + l_edges[1::]) / 2
    Dl_kSZ = l_bins * (l_bins + 1) * Cl_kSZ / (2 * np.pi)
    
    return l_bins, Dl_kSZ, Cl_kSZ

def get_Dl_kSZ_postreion(l_arr, zend, tau, omega_b, h, sigma_8):
    ### CSF model of Shaw, Rudd & Nagai (2012), see their Table 3
    lvals = np.linspace(1000, 10000, num=10)
    Dl0 = np.array([1.43, 2.00, 2.19, 2.27, 2.32, 2.36, 2.40, 2.44, 2.48, 2.52])
    
    hval = 0.7
    alpha_h = np.array([1.09, 1.46, 1.65, 1.78, 1.87, 1.94, 2.00, 2.06, 2.10, 2.14])
    
    s8val = 0.82
    alpha_s8 = np.array([4.19, 4.33, 4.46, 4.57, 4.67, 4.76, 4.83, 4.89, 4.95, 4.99])
    
    ombval = 0.047
    alpha_omb = np.array([2.31, 2.18, 2.12, 2.09, 2.06, 2.04, 2.02, 2.01, 2.00, 1.99])
    
    zeval = 10.0
    alpha_ze = np.array([0.63, 0.66, 0.64, 0.60, 0.55, 0.52, 0.48, 0.45, 0.42, 0.40])
    
    tauval = 0.076
    alpha_tau = np.array([0.43, 0.45, 0.44, 0.41, 0.38, 0.35, 0.33, 0.31, 0.29, 0.27])
    
    Dlvals = Dl0
    Dlvals *= (h / hval) ** alpha_h
    Dlvals *= (sigma_8 / s8val) ** alpha_s8
    Dlvals *= (omega_b / ombval) ** alpha_omb
    Dlvals *= (zend / zeval) ** alpha_ze
    Dlvals *= (tau / tauval) ** alpha_tau
    Dlvals *= 1.22 ## Helium
    
    Dl_arr = np.interp(l_arr, lvals, Dlvals)
    
    
    return Dl_arr
