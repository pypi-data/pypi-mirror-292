
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
### make sure you have run the appropriate MUSIC simulations before executing this example

data_path_arr = np.char.array(['/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N256_L256.0_MUSIC_2LPT-r1', '/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N128_L128.0_MUSIC_2LPT-r1'])
dx_arr = np.array([4.0, 8.0]) #### cMpc / h

data_root = 'snap'
log10Mmin = 9.0
zeta = 15.0
l_edges = np.linspace(1000, 5000, num=51)

convolve = True

col_arr = np.char.array(['tab:red', 'tab:blue'])
ls_arr = np.char.array(['-', '--'])

for sim_loop, data_path in enumerate(data_path_arr):
    outpath = data_path + '/script_files'  ## directory where the script-related files were stored

    for ngrid_loop, dx in enumerate(dx_arr):
        

        z_arr = np.array([])
        QHII_mean_arr = np.array([])
        Pqperp_binned_z_arr = np.empty( shape=(0, len(l_edges)-1) )
        Pqperp_wocorr_binned_z_arr = np.empty( shape=(0, len(l_edges)-1) )



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
                    ngrid = int(np.rint(gadget_data.box / dx))
                    print ('box, ngrid = ', gadget_data.box, ngrid)

                dens_fields = script.matter_fields(gadget_data, ngrid, outpath, overwrite_files=False)
                ionmap = script.ionization_map(dens_fields)

                fcoll_arr = dens_fields.get_fcoll_for_Mmin(log10Mmin)
                fcoll_mean = np.mean(fcoll_arr * (1 + dens_fields.densitycontr_arr))
                qi_arr = ionmap.get_qi(zeta * fcoll_arr)
                #print (np.min(fcoll_arr), np.max(fcoll_arr), np.min(dens_fields.densitycontr_arr), np.max(dens_fields.densitycontr_arr))
                Delta_HII_arr = qi_arr * (1 + dens_fields.densitycontr_arr)
                QHII_mean = np.mean(Delta_HII_arr)
                box = gadget_data.box

                z_arr = np.append(z_arr, gadget_data.z)
                QHII_mean_arr = np.append(QHII_mean_arr, QHII_mean)
                #print ('z, mean ionized fraction:', gadget_data.z, QHII_mean)

                dens_fields.initialize_powspec()

                powspec_qperp_binned, kount, k_l_edges = ionmap.get_binned_powspec_qperp(qi_arr, l_edges, convolve=convolve)
                k_l_bins = (k_l_edges[:-1:] + k_l_edges[1::]) / 2

                # Delta_HI_z_arr = np.concatenate((Delta_HI_z_arr, [Delta_HI_arr[:,ygrid,:]]), axis = 0)

                #k_edges, k_bins = dens_fields.set_k_edges(nbins=int(np.rint(np.log(ngrid / 2) / (0.1 * 1.442))), log_bins=True) ### dlnk of 0.07
                k_edges, k_bins = dens_fields.set_k_edges(kmin=3*np.pi/box, kmax=(ngrid+1)*np.pi/box, nbins=int(np.rint(ngrid / 2 - 1)), log_bins=False)
                #print ('k_bins:', k_bins)
                P_ee_binned, kount = ionmap.get_binned_powspec(Delta_HII_arr, k_edges, convolve=convolve)
                P_mm_binned, kount = ionmap.get_binned_powspec(dens_fields.densitycontr_arr, k_edges, convolve=convolve)
                P_halo_binned, kount = ionmap.get_binned_powspec(fcoll_arr * (1 + dens_fields.densitycontr_arr) / fcoll_mean, k_edges, convolve=convolve)
                #print (gadget_data.z, QHII_mean, k_edges[0], k_edges[1], kount[0], k_bins[0], P_ee_binned[0] / P_mm_binned[0], (QHII_mean) ** 2 * P_halo_binned[0] / P_mm_binned[0], 1 - P_ee_binned[0] / ((QHII_mean) ** 2 * P_halo_binned[0]))
                #print ('kount:', kount)
                #print (k_bins[0] - (k_bins[1] - k_bins[0]), k_edges[0] - (k_edges[1] - k_edges[0]) / 2, 2 * np.pi / box)
                print ('z, mean ionized fraction:', gadget_data.z, QHII_mean)

                #k_arr = k_bins
                box_large = 8192.0
                Pqperp_missing = script_fortran_modules.ionization_map.add_missing_pqperp_ksz(gadget_data.z, QHII_mean, box, k_l_bins, k_bins, P_ee_binned, P_mm_binned, P_halo_binned, omega_m, omega_l, h, sigma_8, ns, omega_b, box_large)
                #print (gadget_data.z, QHII_mean, P_mm_binned / Pqperp_missing)
                #plt.plot(k_bins, Pqperp_missing, label='lin'+str(gadget_data.z))
                #plt.plot(k_bins, P_mm_binned, label='mat'+str(gadget_data.z))

                Pqperp_wocorr_binned_z_arr = np.concatenate((Pqperp_wocorr_binned_z_arr, [powspec_qperp_binned]), axis=0)
                #print (powspec_qperp_binned[0], Pqperp_missing[0], k_l_bins[0])
                powspec_qperp_binned += Pqperp_missing
                Pqperp_binned_z_arr = np.concatenate((Pqperp_binned_z_arr, [powspec_qperp_binned]), axis=0)
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
        #print (l_bins, Dl_kSZ_patchy)
        l_bins, Dl_kSZ_patchy_wocorr, _ = script.utils.get_Dl_kSZ_patchy(z_arr, Pqperp_wocorr_binned_z_arr, tau_arr, l_edges, omega_m, omega_l, omega_b, YHe, h)
        #print (l_bins, Dl_kSZ_patchy_wocorr)

        ### uncomment the following block if post reionization contribution is needed
        # z1 = z_arr[QHII_mean_arr > 0.99][0]
        # z2 = z_arr[QHII_mean_arr <= 0.99][-1]
        # Q1 = QHII_mean_arr[QHII_mean_arr > 0.99][0]
        # Q2 = QHII_mean_arr[QHII_mean_arr <= 0.99][-1]
        # zend = ((z2 - z1) * 0.99 + z1 * Q2 - z2 * Q1) / (Q2 - Q1)
        # tau = tau_arr[0]
        # print (zend, tau, omega_b, h, sigma_8)
        # Dl_kSZ_postreion = script.utils.get_Dl_kSZ_postreion(l_bins, zend, tau, omega_b, h, sigma_8)

        plt.plot(l_bins, Dl_kSZ_patchy, label=str(box) + ', ' + str(dx) + '(with missing power)', ls=ls_arr[ngrid_loop], c=col_arr[sim_loop], linewidth=2.0)
        plt.plot(l_bins, Dl_kSZ_patchy_wocorr, label=str(box) + ', ' + str(dx) + '(w/o missing power)', ls=ls_arr[ngrid_loop], c=col_arr[sim_loop], linewidth=0.5)
        #plt.plot(l_bins, Dl_kSZ_postreion, label='post reion')

plt.title(r'box ($h^{-1}$ cMpc), grid cell size ($h^{-1}$ cMpc)')
plt.xlabel(r'$\ell$')
plt.ylabel(r'$D_{\ell}^{\mathrm{kSZ}} \, (\mu \mathrm{K}^2)$')
plt.legend()
#plt.xscale('log')
#plt.yscale('log')
plt.show()
