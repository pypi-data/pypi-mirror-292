
from __future__ import print_function

import numpy as np
import os
import configparser

import matplotlib.pyplot as plt
# from matplotlib.image import NonUniformImage
import matplotlib

import script
import script_fortran_modules

## Use the directory where you have stored the MUSIC output files
data_path = '/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N128_L128.0_MUSIC_2LPT-r1'
data_root = 'snap'
outpath = data_path + '/script_files'  ## directory where the script-related files were stored


### Set some parameters. log10Mmin and zeta set the reionization history
ngrid = 64
log10Mmin = 9.0
zeta = 15.0
l_edges = np.linspace(1000, 5000, num=51)

z_arr = np.array([])
QHII_mean_arr = np.array([])
Pqperp_binned_z_arr = np.empty( shape=(0, len(l_edges)-1) )


convolve = True

loop = 0
snap = 0
delta_snap = 1


### looping over all the MUSIC output files in the directory
while(True):
    snap_str = '{:03d}'.format(snap)
    gadget_snap = data_path + "/" + data_root + "_" + snap_str

    if (loop == 0):
        config = configparser.ConfigParser()
        config.read(data_path + '/music_000.info')
        omega_b = float(config['cosmology']['Omega_b'])
        sigma_8 = float(config['cosmology']['sigma_8'])
        ns = float(config['cosmology']['nspec'])
        #print (omega_b, sigma_8, ns)

    if (os.path.exists(gadget_snap)):

        gadget_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=sigma_8, ns=ns, omega_b=omega_b)
        if (loop == 0):
            omega_m = gadget_data.cosmo.omega_m
            omega_l = gadget_data.cosmo.omega_l
            h = gadget_data.cosmo.h
            YHe = gadget_data.cosmo.YHe

        dens_fields = script.matter_fields(gadget_data, ngrid, outpath, overwrite_files=False)
        ionmap = script.ionization_map(dens_fields)

        fcoll_arr = dens_fields.get_fcoll_for_Mmin(log10Mmin)
        qi_arr = ionmap.get_qi(zeta * fcoll_arr)
        #print (np.min(fcoll_arr), np.max(fcoll_arr), np.min(dens_fields.densitycontr_arr), np.max(dens_fields.densitycontr_arr))
        Delta_HII_arr = qi_arr * (1 + dens_fields.densitycontr_arr)

        box = gadget_data.box

        z_arr = np.append(z_arr, gadget_data.z)
        QHII_mean_arr = np.append(QHII_mean_arr, np.mean(Delta_HII_arr))
        print ('z, mean ionized fraction:', gadget_data.z, np.mean(Delta_HII_arr))

        dens_fields.initialize_powspec()
        powspec_qperp_binned, kount, k_l_edges = ionmap.get_binned_powspec_qperp(qi_arr, l_edges, convolve=convolve)
        Pqperp_binned_z_arr = np.concatenate((Pqperp_binned_z_arr, [powspec_qperp_binned]), axis=0)
        # Delta_HI_z_arr = np.concatenate((Delta_HI_z_arr, [Delta_HI_arr[:,ygrid,:]]), axis = 0)

    else: ## when we do not find the next snapshot
        break

    loop += 1
    snap += delta_snap

#print ("k bin values: ", k_bins)

num_maps = loop

### check if the history is sensible! compute CMB optical depth
tau_arr = script.utils.get_tau(z_arr, QHII_mean_arr, omega_m, omega_l, omega_b, h, YHe)
print ('CMB tau for the reionization hstory: ', tau_arr[0])

l_bins, Dl_kSZ_patchy, _ = script.utils.get_Dl_kSZ_patchy(z_arr, Pqperp_binned_z_arr, tau_arr, l_edges, omega_m, omega_l, omega_b, YHe, h)

### linear interpolation to compute zend
z1 = z_arr[QHII_mean_arr > 0.99][0]
z2 = z_arr[QHII_mean_arr <= 0.99][-1]
Q1 = QHII_mean_arr[QHII_mean_arr > 0.99][0]
Q2 = QHII_mean_arr[QHII_mean_arr <= 0.99][-1]
zend = ((z2 - z1) * 0.99 + z1 * Q2 - z2 * Q1) / (Q2 - Q1)
tau = tau_arr[0]
#print (zend, tau, omega_b, h, sigma_8)
Dl_kSZ_postreion = script.utils.get_Dl_kSZ_postreion(l_bins, zend, tau, omega_b, h, sigma_8)


plt.plot(l_bins, Dl_kSZ_patchy, label='patchy reionization')
plt.plot(l_bins, Dl_kSZ_postreion, label='post reionization')
plt.plot(l_bins, Dl_kSZ_patchy + Dl_kSZ_postreion, label='total')

plt.xlabel(r'$\ell$')
plt.ylabel(r'$D_{\ell}^{\mathrm{kSZ}} \, (\mu \mathrm{K}^2)$')
plt.legend()
plt.show()
